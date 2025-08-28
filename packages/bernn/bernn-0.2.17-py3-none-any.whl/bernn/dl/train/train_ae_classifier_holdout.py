#!/usr/bin/python3

import os
import matplotlib
from bernn.utils.pool_metrics import log_pool_metrics
import uuid
import shutil
import matplotlib.pyplot as plt
import numpy as np
import random
# import json
import copy
import torch
from torch import nn
# from sklearn import metrics
from tensorboardX import SummaryWriter
from ax.service.managed_loop import optimize
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from bernn.ml.train.params_gp import linsvc_space
from bernn.dl.models.pytorch.utils.loggings import TensorboardLoggingAE, log_input_ordination
from bernn.dl.models.pytorch.utils.utils import LogConfusionMatrix
from bernn.dl.models.pytorch.utils.dataset import get_loaders, get_loaders_no_pool
from bernn.utils.utils import scale_data
from bernn.dl.models.pytorch.utils.utils import get_optimizer, get_empty_dicts, get_empty_traces, \
    log_traces, get_best_values, add_to_logger, add_to_neptune, add_to_mlflow
import mlflow
import warnings
import neptune
from datetime import datetime
from bernn.dl.train.train_ae import TrainAE
from typing import Union
from bernn.config.training_config import TrainingConfig

matplotlib.use('Agg')
CUDA_VISIBLE_DEVICES = ""
NEPTUNE_API_TOKEN = os.environ.get("NEPTUNE_API_TOKEN")
NEPTUNE_PROJECT_NAME = "BERNN"

# import StratifiedGroupKFold
# from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
# from bernn.utils.utils import get_unique_labels

# from fastapi import BackgroundTasks, FastAPI
# from threading import Thread

# app = FastAPI()

warnings.filterwarnings("ignore")

random.seed(1)
torch.manual_seed(1)
np.random.seed(1)


def log_num_neurons(run, n_neurons, init_n_neurons):
    """
    Log the number of neurons in the model to Neptune.

    Args:
        run: The Neptune run object.
        n_neurons: Dictionary of current neuron counts per layer (flattened).
        init_n_neurons: Dictionary of initial neuron counts per layer (nested).
    """
    for key, count in n_neurons.items():
        if key in ["total", "total_neurons", "total_remaining"]:
            run["n_neurons/total"].log(count)
            denom = init_n_neurons.get("total") or init_n_neurons.get("total_neurons")
            if denom:
                run["n_neurons/relative_total"].log(count / denom)
            continue

        if '.' not in key:
            continue  # unexpected format, skip

        layer_abbr, sublayer = key.split(".")
        layer_key = {"enc": "encoder2", "dec": "decoder2"}.get(layer_abbr, layer_abbr)

        run[f"n_neurons/{layer_key}/{sublayer}"].log(count)

        try:
            init_count = init_n_neurons[layer_key][sublayer]
            run[f"n_neurons/{layer_key}/relative_{sublayer}"].log(count / init_count)
        except (KeyError, ZeroDivisionError):
            pass


class TrainAEClassifierHoldout(TrainAE):
    def __init__(self,
                 config: Union[TrainingConfig, object, None] = None,
                 path: str = './data',
                 fix_thres: float = -1,
                 load_tb: bool = False,
                 log_metrics: bool = False,
                 keep_models: bool = True,
                 log_inputs: bool = False,
                 log_plots: bool = False,
                 log_tb: bool = False,
                 log_neptune: bool = False,
                 log_mlflow: bool = False,
                 log_dvclive: bool = False,
                 groupkfold: bool = True,
                 pools: bool = False,
                 **kwargs):
        """
        Args:
            config: TrainingConfig object, legacy args, or None
            path: Path to the data
            ... (other args as before)
        """
        if config is None:
            self.config = TrainingConfig(**kwargs)
            args = self.config
        elif isinstance(config, TrainingConfig):
            self.config = config
            args = config
        else:
            try:
                self.config = TrainingConfig.from_args(config)
                args = config
            except Exception:
                args = config
                self.config = TrainingConfig()
        super().__init__(args, path, fix_thres, load_tb, log_metrics, keep_models, log_inputs, log_plots, log_tb,
                         log_neptune, log_mlflow, log_dvclive, groupkfold, pools)

    # TODO SHOULD BE IN PARENT CLASS
    def launch_mlflow(self, params):
        mlflow.set_experiment(
            self.args.exp_id,
        )
        try:
            mlflow.start_run()
        except Exception as e:
            print(f"Error starting mlflow run: {e}")
            mlflow.end_run()
            mlflow.start_run()
        mlflow.log_params({
            "inputs_type": self.args.csv_file.split(".csv")[0],
            "best_unique": self.args.best_features_file.split(".tsv")[0],
            "tied_weights": self.args.tied_weights,
            "random_recs": self.args.random_recs,
            "train_after_warmup": self.args.train_after_warmup,
            "warmup_after_warmup": self.args.warmup_after_warmup,
            "dloss": self.args.dloss,
            "predict_tests": self.args.predict_tests,
            "variational": self.args.variational,
            "zinb": self.args.zinb,
            "threshold": self.args.threshold,
            "rec_loss_type": self.args.rec_loss,
            "bad_batches": self.args.bad_batches,
            "remove_zeros": self.args.remove_zeros,
            "parameters": params,
            "scaler": params['scaler'],
            "csv_file": self.args.csv_file,
            "model_name": self.args.model_name,
            "n_meta": self.args.n_meta,
            "n_emb": self.args.embeddings_meta,
            "groupkfold": self.args.groupkfold,
            "foldername": self.foldername,
            "use_mapping": self.args.use_mapping,
            "dataset_name": self.args.dataset,
            "n_agg": self.args.n_agg,
            "lr": params['lr'],
            "wd": params['wd'],
            "dropout": params['dropout'],
            "margin": params['margin'],
            "smooth": params['smoothing'],
            "layer1": params['layer1'],
            "layer2": params['layer2'],
            "gamma": self.gamma,
            "beta": self.beta,
            "zeta": self.zeta,
            "thres": params['thres'],
            "nu": params['nu'],
            "kan": self.args.kan,
            "l1": self.l1,
            "reg_entropy": self.reg_entropy,
            "use_l1": self.args.use_l1,
            "clip_val": self.args.clip_val,
            "update_grid": self.args.update_grid,
            "prune_threshold": self.args.prune_threshold,
        })

    # TODO SHOULD BE IN PARENT CLASS
    def launch_neptune(self, params):
        # Create a Neptune run object
        run = neptune.init_run(
            project=NEPTUNE_PROJECT_NAME,
            api_token=NEPTUNE_API_TOKEN,
        )  # your credentials
        run["dataset"].track_files(f"{self.path}/{self.args.csv_file}")
        run["metadata"].track_files(
            f"{self.path}/subjects_experiment_ATN_verified_diagnosis.csv"
        )
        # Track metadata and hyperparameters by assigning them to the run
        run["inputs_type"] = self.args.csv_file.split(".csv")[0]
        run["best_unique"] = self.args.best_features_file.split(".tsv")[0]
        run["use_valid"] = self.args.use_valid
        run["use_test"] = self.args.use_test
        run["tied_weights"] = self.args.tied_weights
        run["random_recs"] = self.args.random_recs
        run["train_after_warmup"] = self.args.train_after_warmup
        run["dloss"] = self.args.dloss
        run["predict_tests"] = self.args.predict_tests
        run["variational"] = self.args.variational
        run["zinb"] = self.args.zinb
        run["threshold"] = self.args.threshold
        run["rec_loss_type"] = self.args.rec_loss
        run["strategy"] = self.args.strategy
        run["bad_batches"] = self.args.bad_batches
        run["remove_zeros"] = self.args.remove_zeros
        run["parameters"] = params
        run["csv_file"] = self.args.csv_file
        run["model_name"] = 'ae_classifier_holdout'
        run["n_meta"] = self.args.n_meta
        run["n_emb"] = self.args.embeddings_meta
        run["groupkfold"] = self.args.groupkfold
        run["embeddings_meta"] = self.args.embeddings_meta
        run["foldername"] = self.foldername
        run["use_mapping"] = self.args.use_mapping
        run["dataset_name"] = self.args.dataset
        run["n_agg"] = self.args.n_agg
        run["kan"] = self.args.kan

        return run

    def get_ordered_layers(self, params):
        """Extract layer parameters from params dictionary, order them, and store in a new dictionary.

        Args:
            params (dict): Dictionary containing model parameters including layer sizes

        Returns:
            dict: Ordered dictionary of layer parameters
        """
        # Extract layer parameters and sort them
        layer_params = {k: v for k, v in params.items() if k.startswith('layer')}
        ordered_layers = dict(sorted(layer_params.items(),
                                     key=lambda x: int(x[0].replace('layer', ''))))
        return ordered_layers

    def train(self, params):
        """
        Args:
            params: hyperparameters
        Returns:
            best valid classification loss (float) for Ax (minimize)
        """
        start_time = datetime.now()
        params = self.make_params(params)
        optimizer_type = 'adam'
        metrics = {'pool_metrics': {}}
        loggers = {'cm_logger': LogConfusionMatrix(self.complete_log_path)}
        print(f'See results using: tensorboard --logdir={self.complete_log_path} --port=6006')

        os.makedirs(self.hparams_filepath, exist_ok=True)
        self.args.model_name = 'ae_classifier_holdout'
        if self.log_tb:
            loggers['tb_logging'] = TensorboardLoggingAE(self.hparams_filepath, params,
                                                         variational=self.args.variational,
                                                         zinb=self.args.zinb,
                                                         tw=self.args.tied_weights,
                                                         dloss=self.args.dloss,
                                                         tl=0,  # to remove, useless now
                                                         pseudo=self.args.predict_tests,
                                                         train_after_warmup=self.args.train_after_warmup,
                                                         berm='none',  # to remove, useless now
                                                         args=self.args)
        else:
            model = None
            run = None

        if self.log_neptune:
            run = self.launch_neptune(params)

        if self.log_mlflow:
            self.launch_mlflow(params)
        if not self.log_mlflow and not self.log_neptune:
            model = None
            run = None
        seed = 0
        combinations = []
        h = 0
        best_closses = []
        best_mccs = []
        while h < self.args.n_repeats:
            # prune_threshold = self.args.prune_threshold
            print(f'Rep: {h}')
            epoch = 0
            self.best_loss = np.inf
            self.best_closs = np.inf
            self.best_dom_loss = np.inf
            self.best_dom_acc = np.inf
            self.best_acc = 0
            self.best_mcc = -1
            self.warmup_counter = 0
            self.warmup_b_counter = 0
            self.warmup_disc_b = False
            # best_acc = 0
            # best_mcc = -1
            # warmup_counter = 0
            # warmup_b_counter = 0
            self.get_data(h)
            self.n_cats = len(np.unique(self.data['cats']['all']))  # + 1  # for pool samples
            if self.args.groupkfold:
                combination = list(np.concatenate((np.unique(self.data['batches']['train']),
                                                   np.unique(self.data['batches']['valid']),
                                                   np.unique(self.data['batches']['test']))))
                seed += 1
                if combination not in combinations:
                    combinations += [combination]
                else:
                    continue
            # print(combinations)
            self.columns = self.data['inputs']['all'].columns
            h += 1
            self.make_samples_weights()
            # event_acc is used to verify if the hparams have already been tested. If they were,
            # the best classification loss is retrieved and we go to the next trial
            event_acc = EventAccumulator(self.hparams_filepath)
            event_acc.Reload()
            if len(event_acc.Tags()['tensors']) > 2 and self.load_tb:
                # try:
                #     best_acc = get_best_acc_from_tb(event_acc)
                # except:
                pass
            else:
                # If thres > 0, features that are 0 for a proportion of samples smaller than thres are removed
                # data = self.keep_good_features(thres)

                # Transform the data with the chosen scaler
                data = copy.deepcopy(self.data)
                data, self.scaler = scale_data(params['scaler'], data, self.args.device)

                # feature_selection = get_feature_selection_method('mutual_info_classif')
                # mi = feature_selection(data['inputs']['train'], data['cats']['train'])
                for g in list(data['inputs'].keys()):
                    data['inputs'][g] = data['inputs'][g].round(4)
                # Gets all the pytorch dataloaders to train the models
                if self.pools:
                    loaders = get_loaders(data, self.args.random_recs, self.samples_weights, self.args.dloss, None,
                                          None, bs=self.args.bs)
                else:
                    loaders = get_loaders_no_pool(data, self.args.random_recs, self.samples_weights, self.args.dloss,
                                                  None, None, bs=self.args.bs)

                if h == 1 or self.args.kan == 1:

                    ae = self.ae(
                        data['inputs']['all'].shape[1],
                        is_sigmoid=self.args.use_sigmoid,
                        n_batches=self.n_batches,
                        nb_classes=self.n_cats,
                        mapper=self.args.use_mapping,
                        layers=self.get_ordered_layers(params),
                        n_layers=self.args.n_layers,
                        n_meta=self.args.n_meta,
                        n_emb=self.args.embeddings_meta,
                        dropout=params['dropout'],
                        variational=self.args.variational,
                        conditional=False,
                        zinb=self.args.zinb,
                        add_noise=0,
                        tied_weights=self.args.tied_weights,
                        device=self.args.device,
                        prune_threshold=params['prune_threshold'],
                        update_grid=self.args.update_grid,
                    ).to(self.args.device)
                    ae.mapper.to(self.args.device)
                    ae.dec.to(self.args.device)
                    n_neurons = ae.prune_model_paperwise(False, False, weight_threshold=params['prune_threshold'])
                    init_n_neurons = ae.count_n_neurons()
                    # if self.args.embeddings_meta > 0:
                    #     n_meta = self.n_meta
                    shap_ae = self.shap_ae(
                        data['inputs']['all'].shape[1],
                        is_sigmoid=self.args.use_sigmoid,
                        n_batches=self.n_batches,
                        nb_classes=self.n_cats,
                        mapper=self.args.use_mapping,
                        layers=self.get_ordered_layers(params),
                        n_layers=self.args.n_layers,
                        n_meta=self.args.n_meta,
                        n_emb=self.args.embeddings_meta,
                        dropout=params['dropout'],
                        variational=self.args.variational, conditional=False,
                        zinb=self.args.zinb, add_noise=0, tied_weights=self.args.tied_weights,
                        device=self.args.device,
                        # prune_threshold=params['prune_threshold'],
                        # update_grid=self.args.update_grid
                    ).to(self.args.device)
                    shap_ae.mapper.to(self.args.device)
                    shap_ae.dec.to(self.args.device)
                else:
                    ae.random_init(nn.init.xavier_uniform_)
                loggers['logger_cm'] = SummaryWriter(f'{self.complete_log_path}/cm')
                loggers['logger'] = SummaryWriter(f'{self.complete_log_path}/traces')
                sceloss, celoss, mseloss, triplet_loss = self.get_losses(
                    params['scaler'], params['smoothing'], params['margin'], self.args.dloss
                )

                optimizer_ae = get_optimizer(ae, params['lr'], params['wd'], optimizer_type)

                # Used only if bdisc==1
                optimizer_b = get_optimizer(ae.dann_discriminator, 1e-2, 0, optimizer_type)

                self.hparams_names = [x.name for x in linsvc_space]
                if self.log_inputs and not self.logged_inputs:
                    data['inputs']['all'].to_csv(
                        f'{self.complete_log_path}/{self.args.berm}_inputs.csv')
                    if self.log_neptune:
                        run["inputs.csv"].track_files(f'{self.complete_log_path}/{self.args.berm}_inputs.csv')
                    log_input_ordination(loggers['logger'], data, self.scaler, epoch)
                    if self.pools:
                        metrics = log_pool_metrics(data['inputs'], data['batches'], data['labels'], loggers, epoch,
                                                   metrics, 'inputs')
                    self.logged_inputs = True

                values, best_values, _, best_traces = get_empty_dicts()

                early_stop_counter = 0
                best_vals = values
                if h > 1:  # or warmup_counter == 100:
                    ae.load_state_dict(torch.load(f'{self.complete_log_path}/warmup.pth'))
                    print("\n\nNO WARMUP\n\n")
                if h == 1:
                    for epoch in range(0, self.args.warmup):
                        no_error, ae, warmup = self.warmup_loop(optimizer_ae, None, ae, celoss, loaders['all'],
                                                                triplet_loss, mseloss, True, epoch,
                                                                optimizer_b, values, loggers, loaders, run, self.args.use_mapping)

                        if not warmup:
                            break
                        # End-of-epoch update (skip during warmup if set)
                        if args.update_grid and epoch >= args.update_grid_warmup:
                            # Safely call grid updates on the AE model if available (KAN only)
                            try:
                                updated = ae.update_grids()
                                print(f"[epoch {epoch}] Updated {updated} KAN grids")
                            except Exception:
                                pass

                for epoch in range(0, self.args.n_epochs):
                    if early_stop_counter == self.args.early_stop:
                        if self.verbose > 0:
                            print('EARLY STOPPING.', epoch)
                        break
                    lists, traces = get_empty_traces()

                    if self.args.warmup_after_warmup:
                        no_error, ae, warmup = self.warmup_loop(optimizer_ae, None, ae, celoss, loaders['all'], triplet_loss, mseloss,
                                         False, epoch,
                                         optimizer_b, values, loggers, loaders, run, self.args.use_mapping)
                    if not self.args.train_after_warmup:
                        ae = self.freeze_all_but_clayers(ae)
                    losses = {
                        "mseloss": mseloss,
                        "celoss": sceloss,
                    }
                    closs = self.loop_train('train', optimizer_ae, ae, None, losses,
                                            loaders['train'], lists, traces, nu=params['nu'])

                    if torch.isnan(closs):
                        print("NAN LOSS")
                        break
                    ae.eval()
                    ae.mapper.eval()

                    # Below is the loop for all sets
                    with torch.no_grad():
                        for group in list(data['inputs'].keys()):
                            if group in ['all', 'all_pool']:
                                continue
                            closs, lists, traces = self.loop(group, optimizer_ae, ae, sceloss,
                                                             loaders[group], lists, traces, nu=0)
                        # closs, _, _ = self.loop('train', optimizer_ae, ae, sceloss,
                        #                         loaders['train'], lists, traces, nu=0)
                    # Below is the loop for all sets
                    # with torch.no_grad():
                    #     for group in list(data['inputs'].keys()):
                    #         if group in ['all', 'all_pool']:
                    #             continue
                    #         closs, lists, traces = self.loop(group, optimizer_ae, ae, sceloss,
                    #                                          loaders[group], lists, traces, nu=0)
                    #     # IF KAN and pruning threshold > 0, then prune the network
                    #     if self.args.kan and self.args.prune_threshold > 0:
                    #         try:
                    #             self.prune_neurons(ae, self.args.prune_threshold)
                    #         except:
                    #             print("COULD NOT PRUNE")
                    #             # if self.log_mlflow:
                    #             #     mlflow.log_param('finished', 0)
                    #             break
                    #     if self.args.kan and self.args.prune_neurites_threshold > 0:
                    #         self.prune_neurites(ae)
                    #     if self.args.kan and early_stop_counter % 10 == 0 and early_stop_counter > 0:
                    #         self.args.prune_threshold *= 10
                    #         print(f"Pruning threshold: {self.args.prune_threshold}")

                    traces = self.get_mccs(lists, traces)
                    values = log_traces(traces, values)
                    if self.log_tb:
                        try:
                            add_to_logger(values, loggers['logger'], epoch)
                        except Exception as e:
                            print(f"Problem with add_to_logger: {e}")
                    if self.log_neptune:
                        add_to_neptune(values, run)
                    if self.log_mlflow:
                        add_to_mlflow(values, epoch)
                    if np.mean(values['valid']['mcc'][-self.args.n_agg:]) > self.best_mcc and len(
                            values['valid']['mcc']) > self.args.n_agg:
                        print(f"Best Classification Mcc Epoch {epoch}, "
                              f"Acc: {values['test']['acc'][-1]}"
                              f"VALID Mcc: {values['valid']['mcc'][-1]}"
                              f"TEST Mcc: {values['test']['mcc'][-1]}"
                              f"Classification train loss: {values['train']['closs'][-1]},"
                              f" valid loss: {values['valid']['closs'][-1]},"
                              f" test loss: {values['test']['closs'][-1]}")
                        self.best_mcc = np.mean(values['valid']['mcc'][-self.args.n_agg:])
                        torch.save(ae.state_dict(), f'{self.complete_log_path}/model_{h}_state.pth')
                        torch.save(ae, f'{self.complete_log_path}/model_{h}.pth')
                        best_values = get_best_values(values.copy(), ae_only=False, n_agg=self.args.n_agg)
                        best_vals = values.copy()
                        best_vals['rec_loss'] = self.best_loss
                        best_vals['dom_loss'] = self.best_dom_loss
                        best_vals['dom_acc'] = self.best_dom_acc
                        early_stop_counter = 0

                    if values['valid']['acc'][-1] > self.best_acc:
                        print(f"Best Classification Acc Epoch {epoch}, "
                              f"Acc: {values['test']['acc'][-1]}"
                              f"Mcc: {values['test']['mcc'][-1]}"
                              f"Classification train loss: {values['train']['closs'][-1]},"
                              f" valid loss: {values['valid']['closs'][-1]},"
                              f" test loss: {values['test']['closs'][-1]}")

                        self.best_acc = values['valid']['acc'][-1]
                        early_stop_counter = 0

                    if values['valid']['closs'][-1] < self.best_closs:
                        print(f"Best Classification Loss Epoch {epoch}, "
                              f"Acc: {values['test']['acc'][-1]} "
                              f"Mcc: {values['test']['mcc'][-1]} "
                              f"Classification train loss: {values['train']['closs'][-1]}, "
                              f"valid loss: {values['valid']['closs'][-1]}, "
                              f"test loss: {values['test']['closs'][-1]}")
                        self.best_closs = values['valid']['closs'][-1]
                        early_stop_counter = 0
                    else:
                        # if epoch > self.warmup:
                        early_stop_counter += 1

                    if self.args.predict_tests and (epoch % 10 == 0):
                        loaders = get_loaders(self.data, data, self.args.random_recs, self.args.triplet_dloss, ae,
                                              ae.classifier, bs=self.args.bs)
                    if params['prune_threshold'] > 0:
                        n_neurons = ae.prune_model_paperwise(False, False, weight_threshold=params['prune_threshold'])
                        # If save neptune is True, save the model
                        if self.log_neptune:
                            log_num_neurons(run, n_neurons, init_n_neurons)

                best_mccs += [self.best_mcc]

                best_lists, traces = get_empty_traces()
                
                # Verify the model exists
                if not os.path.exists(f'{self.complete_log_path}/model_{h}_state.pth'):
                    # Return a large penalty instead of -1 (keeps Ax consistent)
                    return 1e9
                # Loading best model that was saved during training
                ae.load_state_dict(torch.load(f'{self.complete_log_path}/model_{h}_state.pth'))
                # Need another model because the other cant be use to get shap values
                if h == 1:
                    shap_ae.load_state_dict(torch.load(f'{self.complete_log_path}/model_{h}_state.pth'))
                # ae.load_state_dict(sd)
                ae.eval()
                shap_ae.eval()
                ae.mapper.eval()
                shap_ae.mapper.eval()
                with torch.no_grad():
                    for group in list(data['inputs'].keys()):
                        # if group in ['all', 'all_pool']:
                        #     continue
                        closs, best_lists, traces = self.loop(group, None, ae, sceloss,
                                                              loaders[group], best_lists, traces, nu=0, mapping=False)
                # if self.log_neptune:
                #     model["model"].upload(f'{self.complete_log_path}/model_{h}_state.pth')
                #     model["validation/closs"].log(self.best_closs)
                best_closses += [self.best_closs]
                # logs things in the background. This could be problematic if the logging
                # takes more time than each iteration of repetitive holdout
                # daemon = Thread(target=self.log_rep, daemon=True, name='Monitor',
                #                 args=[best_lists, best_vals, best_values, traces, model, metrics, run, cm_logger, ae,
                #                       shap_ae, h,
                #                       epoch])
                # daemon.start()
                self.log_rep(best_lists, best_vals, best_values, traces, metrics, run, loggers, ae,
                             shap_ae, h, epoch)

        # Logging every model is taking too much resources and it makes it quite complicated to get information when
        # Too many runs have been made. This will make the notebook so much easier to work with
        if np.mean(best_mccs) > self.best_mcc:
            try:
                if os.path.exists(
                        f'logs/best_models/ae_classifier_holdout/{self.args.dataset}/'
                        f'{self.args.dloss}_vae{self.args.variational}'
                ):
                    shutil.rmtree(
                        f'logs/best_models/ae_classifier_holdout/{self.args.dataset}/'
                        f'{self.args.dloss}_vae{self.args.variational}',
                        ignore_errors=True)
                shutil.copytree(f'{self.complete_log_path}',
                                f'logs/best_models/ae_classifier_holdout/'
                                f'{self.args.dataset}/{self.args.dloss}_vae{self.args.variational}')
                # print("File copied successfully.")

            # If source and destination are same
            except shutil.SameFileError:
                # print("Source and destination represents the same file.")
                pass
            self.best_mcc = np.mean(best_mccs)

        # Logs confusion matrices in the background. Also runs RandomForestClassifier on encoded and reconstructed
        # representations. This should be shorter than the actual calculation of the model above in the function,
        # otherwise the number of threads will keep increasing.
        # daemon = Thread(target=self.logging, daemon=True, name='Monitor', args=[run, cm_logger])
        # daemon.start()
        if self.log_mlflow:
            mlflow.log_param('finished', 1)
        self.logging(run, loggers['cm_logger'])

        if not self.keep_models:
            # shutil.rmtree(f'{self.complete_log_path}/traces', ignore_errors=True)
            # shutil.rmtree(f'{self.complete_log_path}/cm', ignore_errors=True)
            # shutil.rmtree(f'{self.complete_log_path}/hp', ignore_errors=True)
            shutil.rmtree(f'{self.complete_log_path}', ignore_errors=True)
        print('\n\nDuration: {}\n\n'.format(datetime.now() - start_time))
        best_closs = np.mean(best_closses)
        if best_closs < self.best_closs:
            self.best_closs = best_closs
            print("Best closs!")

        # It should not be necessary. To remove once certain the "Too many files open" error is no longer a problem
        plt.close('all')

        return self.best_mcc

    def increase_pruning_threshold(self):
        '''
        increase the pruning threshold
        
        Args:
        -----
            threshold : float
                the amount of increase
        
        Returns:
        --------
            None
        '''
        if self.args.prune_threshold == 0:
            self.args.prune_threshold = 1e-8
        else:
            self.args.prune_threshold *= 10


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    # parser.add_argument('--batch_columns', type=str, default='2,3')
    parser.add_argument('--random_recs', type=int, default=0)
    parser.add_argument('--predict_tests', type=int, default=0)
    parser.add_argument('--early_stop', type=int, default=100)
    parser.add_argument('--early_warmup_stop', type=int, default=0, help='If 0, then no early warmup stop')
    parser.add_argument('--train_after_warmup', type=int, default=1, help="Train autoencoder after warmup")
    parser.add_argument('--warmup_after_warmup', type=int, default=1, help="Warmup after warmup")
    parser.add_argument('--threshold', type=float, default=0.)
    parser.add_argument('--n_epochs', type=int, default=1000)
    parser.add_argument('--n_trials', type=int, default=100)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--rec_loss', type=str, default='mse')
    parser.add_argument('--tied_weights', type=int, default=0)
    parser.add_argument('--variational', type=int, default=0)
    parser.add_argument('--zinb', type=int, default=0)
    parser.add_argument('--use_valid', type=int, default=0, help='Use if valid data is in a seperate file')
    parser.add_argument('--use_test', type=int, default=0, help='Use if test data is in a seperate file')
    parser.add_argument('--use_mapping', type=int, default=1, help="Use batch mapping for reconstruct")
    parser.add_argument('--freeze_ae', type=int, default=0)
    parser.add_argument('--freeze_c', type=int, default=0)
    parser.add_argument('--bdisc', type=int, default=1)
    parser.add_argument('--n_repeats', type=int, default=5)
    parser.add_argument('--dloss', type=str, default='inverseTriplet')
    parser.add_argument('--csv_file', type=str, default='matrix.csv')
    parser.add_argument('--best_features_file', type=str, default='')  # best_unique_genes.tsv
    parser.add_argument('--bad_batches', type=str, default='')  # 0;23;22;21;20;19;18;17;16;15
    parser.add_argument('--remove_zeros', type=int, default=1)
    parser.add_argument('--n_meta', type=int, default=0)
    parser.add_argument('--embeddings_meta', type=int, default=0)
    parser.add_argument('--features_to_keep', type=str, default='features_proteins.csv')
    parser.add_argument('--groupkfold', type=int, default=1)
    parser.add_argument('--dataset', type=str, default='custom')
    parser.add_argument('--path', type=str, default='./data/PXD015912/')
    parser.add_argument('--exp_id', type=str, default='reviewer_exp')
    parser.add_argument('--bs', type=int, default=32, help='Batch size')
    parser.add_argument('--n_agg', type=int, default=1, help='Number of trailing values to get stable valid values')
    parser.add_argument('--n_layers', type=int, default=1, help='N layers for classifier')
    parser.add_argument('--log1p', type=int, default=1, help='log1p the data? Should be 0 with zinb')
    parser.add_argument('--strategy', type=str, default='CU_DEM', help='only for alzheimer dataset')
    parser.add_argument('--pool', type=int, default=1, help='only for alzheimer dataset')
    parser.add_argument('--log_plots', type=int, default=1, help='')
    parser.add_argument('--log_metrics', type=int, default=0, help='')
    parser.add_argument('--controls', type=str, default='', help='Which samples are the controls. Empty for not binary')
    parser.add_argument('--n_features', type=int, default=-1, help='')
    parser.add_argument('--kan', type=int, default=1, help='')
    parser.add_argument('--update_grid', type=int, default=1, help='')
    parser.add_argument('--use_l1', type=int, default=1, help='')
    parser.add_argument('--clip_val', type=float, default=1, help='')
    parser.add_argument('--prune_threshold', type=float, default=1e-4, help='')
    parser.add_argument('--prune_neurites_threshold', type=float, default=0.0, help='')
    parser.add_argument('--prune_network', type=float, default=0, help='')
    parser.add_argument('--log_inputs', type=int, default=0, help='')
    parser.add_argument('--log_neptune', type=int, default=1, help='')
    parser.add_argument('--log_mlflow', type=int, default=0, help='')
    parser.add_argument('--log_dvclive', type=int, default=0, help='')
    parser.add_argument('--log_tb', type=int, default=0, help='')
    parser.add_argument('--keep_models', type=int, default=0, help='')
    parser.add_argument('--update_grid_warmup', type=int, default=0, help='If > 0, then update grid after this many epochs of warmup')
    parser.add_argument('--classif_loss', type=str, default='ce', help='')
    parser.add_argument('--scheduler', type=str, default='ReduceLROnPlateau', help='')
    parser.add_argument('--n_move_valid', type=int, default=0, help='Number of valid samples to move to train')
    parser.add_argument('--n_move_test', type=int, default=0, help='Number of test samples to move to valid')
    args = parser.parse_args()

    if args.kan == 0:
        args.update_grid = 0
        args.update_grid_warmup = 0

    
    # 1. RECOMMENDED: Modern approach with TrainingConfig
    print("=== Modern Configuration Class Approach ===")
    config = TrainingConfig(
        csv_file=args.csv_file,
        exp_id='modern_ae_then_classifier',
        dloss=args.dloss,
        variational=args.variational,
        n_epochs=args.n_epochs,
        device=args.device,
        groupkfold=args.groupkfold,
        n_meta=args.n_meta,
        embeddings_meta=args.embeddings_meta,
        n_layers=args.n_layers,
        n_agg=args.n_agg,
        bad_batches=args.bad_batches,
        remove_zeros=args.remove_zeros,
        dataset=args.dataset,
        kan=args.kan,
        # path=args.path,
        bs=args.bs,
        strategy=args.strategy,
        log1p=args.log1p,
        pool=args.pool,
        update_grid=args.update_grid,
        use_l1=args.use_l1,
        clip_val=args.clip_val,
    )

    # Clean, type-safe instantiation
    trainer_modern = TrainAEClassifierHoldout(
        config=config,
        path='./data',
        log_metrics=args.log_metrics,
        keep_models=args.keep_models,
        log_inputs=args.log_inputs,
        log_plots=args.log_plots,
        log_tb=args.log_tb,
        log_neptune=args.log_neptune,
        log_mlflow=args.log_mlflow,
        log_dvclive=args.log_dvclive,
        pools=False  # TODO redundancy with args.pool
    )

    try:
        mlflow.create_experiment(
            args.exp_id,
            # artifact_location=Path.cwd().joinpath("mlruns").as_uri(),
            # tags={"version": "v1", "priority": "P1"},
        )
    except Exception as e:
        print(f"Error creating experiment: {e}")
        print(f"\n\nExperiment {args.exp_id} already exists\n\n")

    # args.batch_columns = [int(x) for x in args.batch_columns.split(',')]

    train = TrainAEClassifierHoldout(args, args.path, fix_thres=-1, load_tb=False,
                                     log_metrics=args.log_metrics,
                                     keep_models=args.keep_models, log_inputs=args.log_inputs,
                                     log_plots=args.log_plots, log_tb=args.log_tb,
                                     log_neptune=args.log_neptune,
                                     log_mlflow=args.log_mlflow, groupkfold=args.groupkfold,
                                     pools=args.pool)

    # List of hyperparameters getting optimized
    parameters = [
        {"name": "nu", "type": "range", "bounds": [1e-4, 1e2], "log_scale": False},
        {"name": "lr", "type": "range", "bounds": [1e-4, 1e-2], "log_scale": True},
        {"name": "wd", "type": "range", "bounds": [1e-5, 1e-3], "log_scale": True},
        {"name": "smoothing", "type": "range", "bounds": [0., 0.2]},
        {"name": "margin", "type": "range", "bounds": [0., 10.]},
        {"name": "warmup", "type": "range", "bounds": [1, 1000]},
        {"name": "disc_b_warmup", "type": "range", "bounds": [1, 2]},

        {"name": "knn_n_neighbors", "type": "choice", "values": [1, 3, 5, 7, 9, 11]},
        {"name": "dropout", "type": "range", "bounds": [0.0, 0.5]},
        {"name": "scaler", "type": "choice",
         "values": ['minmax', 'standard_per_batch', 'standard', 'robust', 'robust_per_batch']},  # scaler whould be no for zinb
        {"name": "layer2", "type": "range", "bounds": [32, 512]},
        {"name": "layer1", "type": "range", "bounds": [512, 1024]},        
    ]

    # Some hyperparameters are not always required. 
    if args.dloss in ['revTriplet', 'revDANN', 'DANN', 'inverseTriplet', 'normae']:
        # gamma = 0 will ensure DANN is not learned
        parameters += [{"name": "gamma", "type": "range", "bounds": [1e-2, 1e2], "log_scale": True}]
    if args.variational:
        # beta = 0 because useless outside a variational autoencoder
        parameters += [{"name": "beta", "type": "range", "bounds": [1e-2, 1e2], "log_scale": True}]
    if args.zinb:
        # zeta = 0 because useless outside a zinb autoencoder
        parameters += [{"name": "zeta", "type": "range", "bounds": [1e-2, 1e2], "log_scale": True}]
    if args.kan and args.use_l1:
        # zeta = 0 because useless outside a zinb autoencoder
        parameters += [{"name": "reg_entropy", "type": "range", "bounds": [1e-5, 1e-2], "log_scale": True}]
        parameters += [{"name": "reg_entropy", "type": "range", "bounds": [1e-5, 1e-2], "log_scale": True}]
    if args.use_l1:
        parameters += [{"name": "l1", "type": "range", "bounds": [1e-5, 1e-3], "log_scale": True}]
    if args.prune_network:
        parameters += [{"name": "prune_threshold", "type": "range", "bounds": [1e-3, 3e-3], "log_scale": True}]

    # Wrapper for Ax
    def ax_eval(parameterization):
        # try:
        # Ax may give numpy types; ensure plain Python
        param_clean = {k: (int(v) if k.startswith('layer') else float(v) if isinstance(v, (np.floating,)) else v)
                        for k, v in parameterization.items()}
        loss = train.train(param_clean)
        # Guarantee numeric
        loss = float(loss)
        # except Exception as e:
        #     print(f"[AX WARN] Trial failed: {e}")
        #     loss = 1e9
        # Ax optimize() (managed_loop) accepts scalar when objective_name is provided,
        # but explicit dict form is more robust; returning scalar is also fine. Choose one:
        return loss  # scalar OK because objective_name='closs'

    best_parameters, values, experiment, model = optimize(
        parameters=parameters,
        evaluation_function=ax_eval,
        objective_name='closs',
        minimize=True,
        total_trials=args.n_trials,
        random_seed=41
    )

    # fig = plt.figure()
    # render(plot_contour(model=model, param_x="learning_rate", param_y="weight_decay", metric_name='Loss'))
    # fig.savefig('test.jpg')
    # print('Best Loss:', values[0]['loss'])
    # print('Best Parameters:')
    # print(json.dumps(best_parameters, indent=4))