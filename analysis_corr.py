import os
import pdb
import torch
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.pyplot import figure
from sklearn.metrics import mean_squared_error
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

class RebuildLoss():
    def __init__(self):
        pass

    def rebuild_loss_pearson(self, path, epoch_num):
        test_epoch_loss_list = []
        train_epoch_loss_list = []
        test_epoch_pearson_list = []
        train_epoch_pearson_list = []
        min_test_loss = 1000
        min_train_loss = 1000
        max_test_corr = 0
        max_train_corr = 0
        max_test_id = 0
        for i in range(1, epoch_num + 1):
            # TEST LOSS
            try:
                # Attempt to read the file
                test_df = pd.read_csv(path + '/TestPred' + str(i) + '.txt', delimiter=',')
                # Process the DataFrame as needed
                print("Test file read successfully!")
            except Exception as e:
                # If an error occurs, this block of code will run
                print("An error occurred:", e)
                break  # Exit the loop
            test_score_list = list(test_df['Score'])
            test_pred_list = list(test_df['Pred Score'])
            test_epoch_loss = mean_squared_error(test_score_list, test_pred_list)
            test_epoch_loss_list.append(test_epoch_loss)
            test_epoch_pearson = test_df.corr(method = 'pearson')
            test_epoch_corr = test_epoch_pearson['Pred Score'][0]
            test_epoch_pearson_list.append(test_epoch_corr)
            # TRAIN LOSS
            try:
                # Attempt to read the file
                train_df = pd.read_csv(path + '/TrainingPred_' + str(i) + '.txt', delimiter=',')
                # Process the DataFrame as needed
                print("Training file read successfully!")
            except Exception as e:
                # If an error occurs, this block of code will run
                print("An error occurred:", e)
                break  # Exit the loop
            train_score_list = list(train_df['Score'])
            train_pred_list = list(train_df['Pred Score'])
            train_epoch_loss = mean_squared_error(train_score_list, train_pred_list)
            train_epoch_loss_list.append(train_epoch_loss)
            train_epoch_pearson = train_df.corr(method = 'pearson')
            train_epoch_corr = train_epoch_pearson['Pred Score'][0]
            train_epoch_pearson_list.append(train_epoch_corr)
            if test_epoch_loss < min_test_loss:
                min_test_loss = test_epoch_loss
                min_train_loss = train_epoch_loss
            if test_epoch_corr > max_test_corr:
                max_test_corr = test_epoch_corr
                max_train_corr = train_epoch_corr
                max_test_id = i
        best_train_df = pd.read_csv(path + '/TrainingPred_' + str(max_test_id) + '.txt', delimiter=',')
        best_train_df.to_csv(path + '/BestTrainingPred.txt', index=False, header=True)
        best_test_df = pd.read_csv(path + '/TestPred' + str(max_test_id) + '.txt', delimiter=',')
        best_test_df.to_csv(path + '/BestTestPred.txt', index=False, header=True)
        # import pdb; pdb.set_trace()
        print('-------------BEST MODEL ID:' + str(max_test_id) + '-------------')
        print('-------------BEST MODEL ID:' + str(max_test_id) + '-------------')
        print('-------------BEST MODEL ID:' + str(max_test_id) + '-------------')
        print('BEST MODEL TRAIN LOSS: ', min_train_loss)
        print('BEST MODEL PEARSON CORR: ', max_train_corr)
        print('BEST MODEL TEST LOSS: ', min_test_loss)
        print('BEST MODEL PEARSON CORR: ', max_test_corr)
        epoch_pearson_array = np.array(test_epoch_pearson_list)
        epoch_loss_array = np.array(test_epoch_loss_list)
        np.save(path + '/pearson.npy', epoch_pearson_array)
        np.save(path + '/loss.npy', epoch_loss_array)
        return max_test_id


class AnalyseCorr():
    def __init__(self):
        pass

    def pred_result(self, fold_n, epoch_name, dataset, modelname):
        plot_path = './' + dataset + '/plot' + '/' + modelname
        if os.path.exists(plot_path) == False:
            os.mkdir(plot_path)
        ### TRAIN PRED JOINTPLOT
        train_pred_df = pd.read_csv('./' + dataset + '/result/' + modelname + '/' + epoch_name + '/BestTrainingPred.txt')
        try:
            # Attempt to drop the 'Unnamed: 0' column
            train_pred_df.drop(columns=['Unnamed: 0'], inplace=True)
        except KeyError as error:
            # Handle the error if the column is not found
            print(f"Error: {error}. The column 'Unnamed: 0' was not found in the DataFrame.")
        sns.set_style('whitegrid')
        sns.jointplot(data=train_pred_df, x='Score', y='Pred Score', kind='reg')
        train_pearson = train_pred_df.corr(method='pearson')['Pred Score'][0]
        train_score_list = list(train_pred_df['Score'])
        train_pred_list = list(train_pred_df['Pred Score'])
        # import pdb; pdb.set_trace()
        train_loss = mean_squared_error(train_score_list, train_pred_list)
        plt.legend(['Training Pearson =' + str(train_pearson)])
        plt.savefig(plot_path + '/trainpred_corr_' + str(fold_n) + '.png', dpi=300)
        ### TEST PRED JOINTPLOT
        test_pred_df = pd.read_csv('./' + dataset + '/result/' + modelname + '/' + epoch_name + '/BestTestPred.txt')
        try:
            # Attempt to drop the 'Unnamed: 0' column
            test_pred_df.drop(columns=['Unnamed: 0'], inplace=True)
        except KeyError as error:
            # Handle the error if the column is not found
            print(f"Error: {error}. The column 'Unnamed: 0' was not found in the DataFrame.")
        comb_testpred_df = pd.read_csv('./' + dataset + '/filtered_data/split_input_' + str(fold_n) + '.csv')
        print(fold_n, epoch_name, dataset, modelname)
        comb_testpred_df['Pred Score'] = list(test_pred_df['Pred Score'])
        comb_testpred_df.to_csv('./' + dataset + '/result/' + modelname + '/' + epoch_name + '/combine_testpred.csv', index=False, header=True)
        sns.set_style('whitegrid')
        sns.jointplot(data=comb_testpred_df, x='Score', y='Pred Score', kind='reg')
        test_pearson = test_pred_df.corr(method='pearson')['Pred Score'][0]
        test_score_list = list(test_pred_df['Score'])
        test_pred_list = list(test_pred_df['Pred Score'])
        test_loss = mean_squared_error(test_score_list, test_pred_list)
        plt.legend(['Test Pearson =' + str(test_pearson)])
        plt.savefig(plot_path + '/testpred_corr_' + str(fold_n) + '.png', dpi=300)
        print('--- TRAIN ---')
        print('BEST MODEL TRAIN LOSS: ', train_loss)
        print('BEST MODEL TRAIN PEARSON CORR: ', train_pearson)
        print('--- TEST ---')
        print('BEST MODEL TEST LOSS: ', test_loss)
        print('BEST MODEL TEST PEARSON CORR: ', test_pearson)
        ### HISTOGRAM
        hist = test_pred_df.hist(column=['Score', 'Pred Score'], bins=20)
        plt.savefig(plot_path + '/testpred_hist_' + str(fold_n) + '.png', dpi=300)
        ### BOX PLOT
        testpred_df = comb_testpred_df[['Cell Line Name', 'Pred Score']]
        testpred_df['Type'] = ['Prediction Score']*testpred_df.shape[0]
        testpred_df = testpred_df.rename(columns={'Pred Score': 'Drug Score'})
        test_df = comb_testpred_df[['Cell Line Name', 'Score']]
        test_df['Type'] = ['Input Score']*test_df.shape[0]
        test_df = test_df.rename(columns={'Score': 'Drug Score'})
        comb_score_df = pd.concat([testpred_df, test_df])
        comb_score_df = comb_score_df.rename(columns={'Cell Line Name': 'cell_line_name'})
        a4_dims = (20, 15)
        fig, ax = plt.subplots(figsize=a4_dims)
        sns.set_context('paper')
        # import pdb; pdb.set_trace()
        cell_line_list = sorted(list(set(comb_score_df['cell_line_name'])))
        sns.boxplot(ax=ax, x='cell_line_name', y='Drug Score', hue='Type', data=comb_score_df, order=cell_line_list)
        plt.xticks(rotation = 90, ha = 'right')
        plt.savefig(plot_path + '/testpred_compare_cell_line_boxplot_' + str(fold_n) + '.png', dpi=600)
        plt.close('all')
        # plt.show()
        return train_pearson, test_pearson
    
    def pred_all_result(self, num_fold, epoch_num, dataset, modelname, train_mean=True):
        plot_path = './' + dataset + '/plot' + '/' + modelname
        if os.path.exists(plot_path) == False:
            os.mkdir(plot_path)
        ### SCATTER PLOT OF ALL FOLD ON TEST / TRAIN
        # TEST
        test_pred_df_list = []
        for fold_n in range(1, num_fold + 1):
            if fold_n == 1:
                epoch_name = 'epoch_' + str(epoch_num)
            else:
                epoch_name = 'epoch_' + str(epoch_num) + '_' + str(fold_n-1)
            test_pred_df = pd.read_csv('./' + dataset + '/result/' + modelname + '/' + epoch_name + '/combine_testpred.csv')
            test_pred_df_list.append(test_pred_df)
        comb_testpred_df = pd.concat(test_pred_df_list)
        comb_testpred_df = comb_testpred_df.rename(columns={'Cell Line Name': 'cell_line_name'}).reset_index(drop=True)
        print(comb_testpred_df)
        sns.set_style('whitegrid')
        sns.jointplot(data=comb_testpred_df, x='Score', y='Pred Score', kind='reg')
        comb_test_pearson = comb_testpred_df.corr(method='pearson')['Pred Score'][0]
        comb_test_score_list = list(comb_testpred_df['Score'])
        comb_test_pred_list = list(comb_testpred_df['Pred Score'])
        comb_test_loss = mean_squared_error(comb_test_score_list, comb_test_pred_list)
        print('COMBINED MODEL TEST LOSS: ', comb_test_loss)
        print('COMBINED MODEL TEST PEARSON CORR: ', comb_test_pearson)
        plt.legend(['Test Pearson =' + str(comb_test_pearson)])
        plt.savefig(plot_path + '/comb_test_corr.png', dpi=300)
        # TRAIN
        train_pred_df_list = []
        for fold_n in range(1, num_fold + 1):
            if fold_n == 1:
                epoch_name = 'epoch_' + str(epoch_num)
            else:
                epoch_name = 'epoch_' + str(epoch_num) + '_' + str(fold_n-1)
            train_predscore_df = pd.read_csv('./' + dataset + '/result/' + modelname + '/' + epoch_name + '/BestTrainingPred.txt')
            train_pred_df = pd.read_csv('./' + dataset + '/filtered_data/split_train_input_' + str(fold_n) + '.csv')
            train_pred_df['Pred Score'] = list(train_predscore_df['Pred Score'])
            train_pred_df.to_csv('./' + dataset + '/result/' + modelname + '/' + epoch_name + '/combine_trainpred.csv', index=False, header=True)
            train_pred_df_list.append(train_pred_df)
        comb_trainpred_df = pd.concat(train_pred_df_list)
        comb_trainpred_df = comb_trainpred_df.rename(columns={'Cell Line Name': 'cell_line_name'}).reset_index(drop=True)
        print(comb_trainpred_df)
        if train_mean == True:
            comb_trainpred_df = comb_trainpred_df.groupby(['Drug A', 'Drug B', 'cell_line_name']).mean().reset_index()
        print(comb_trainpred_df)
        sns.set_style('whitegrid')
        sns.jointplot(data=comb_trainpred_df, x='Score', y='Pred Score', kind='reg')
        comb_train_pearson = comb_trainpred_df.corr(method='pearson')['Pred Score'][0]
        comb_train_score_list = list(comb_trainpred_df['Score'])
        comb_train_pred_list = list(comb_trainpred_df['Pred Score'])
        comb_train_loss = mean_squared_error(comb_train_score_list, comb_train_pred_list)
        print('COMBINED MODEL TRAIN LOSS: ', comb_train_loss)
        print('COMBINED MODEL TRAIN PEARSON CORR: ', comb_train_pearson)
        plt.legend(['Train Pearson =' + str(comb_train_pearson)])
        plt.savefig(plot_path + '/comb_train_corr.png', dpi=300)
        # plt.show()
        ### BOX PLOT
        testpred_df = comb_testpred_df[['cell_line_name', 'Pred Score']]
        testpred_df['Type'] = ['Prediction Score']*testpred_df.shape[0]
        testpred_df = testpred_df.rename(columns={'Pred Score': 'Drug Score'})
        test_df = comb_testpred_df[['cell_line_name', 'Score']]
        test_df['Type'] = ['Input Score']*test_df.shape[0]
        test_df = test_df.rename(columns={'Score': 'Drug Score'})
        comb_score_df = pd.concat([testpred_df, test_df])
        a4_dims = (15, 15)
        fig, ax = plt.subplots(figsize=a4_dims)
        sns.set_context('paper', font_scale=1.5)
        sns.set_palette("Set2")  
        # cell_line_list = sorted(list(set(comb_score_df['cell_line_name'])))
        final_dl_input_df = pd.read_csv('./' + dataset + '/filtered_data/final_dl_input.csv')
        cell_line_list = final_dl_input_df['Cell Line Name'].value_counts().index
        sns.boxplot(ax=ax, x='cell_line_name', y='Drug Score', hue='Type', data=comb_score_df, order=cell_line_list, width=0.6)
        ax.set_xticklabels(cell_line_list, fontsize=13)  
        plt.xticks(rotation = 90, ha = 'right')
        ax.set_xlabel('Cell Line Names', fontsize=16)  # Adjust the fontsize value as needed
        ax.set_ylabel('Drug Score', fontsize=16)  # Adjust the fontsize value as needed
        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.9)
        plt.savefig(plot_path + '/testpred_compare_cell_line_boxplot_all.png', dpi=600)
        plt.close('all')
        # plt.show()
        # return train_pearson, test_pearson

    def fold_comparison(self, dataset, gcn_decoder_test_list, gat_decoder_test_list, m3net_decoder_test_list,
                        gformer_decoder_test_list, mixhop_decoder_test_list, pna_decoder_test_list, gin_decoder_test_list):
        colors = sns.color_palette("Set2", 7)
        labels = ['1st Fold', '2nd Fold', '3rd Fold', '4th Fold', '5th Fold', 'Average']
        x = np.arange(len(labels))
        width = 0.15 
        print(gcn_decoder_test_list)
        print(gat_decoder_test_list)
        print(gformer_decoder_test_list)
        print(mixhop_decoder_test_list)
        print(pna_decoder_test_list)
        print(gin_decoder_test_list)
        print(m3net_decoder_test_list)
        sns.set_style(style=None)
        gcn = plt.bar(x - 3*width, gcn_decoder_test_list, width, label='GCN Decoder', color=colors[0])
        gat = plt.bar(x - 2*width, gat_decoder_test_list, width, label='GAT Decoder', color=colors[1])
        gformer = plt.bar(x - 1*width, gformer_decoder_test_list, width, label='GraphFormer Decoder', color=colors[2])
        mixhop = plt.bar(x, mixhop_decoder_test_list, width, label='MixHop Decoder', color=colors[3])
        pna = plt.bar(x + 1*width, pna_decoder_test_list, width, label='PNA Decoder', color=colors[4])
        gin = plt.bar(x + 2*width, gin_decoder_test_list, width, label='GIN Decoder', color=colors[5])
        m3net = plt.bar(x + 3*width, m3net_decoder_test_list, width, label='M3NetFlow', color=colors[6])
        plt.ylabel('Pearson Correlation')
        # plt.title('Pearson Correlation Comparison For 3 GNN Models')
        plt.ylim(0.0, 1.0)
        plt.xticks(x, labels=labels)
        plt.legend(loc='upper right', ncol=2)
        plt.savefig('./' + dataset + '/result/fold_comparisons.png', dpi=600)
        # plt.show()

    def dataset_avg_comparison(self, dataset, gcn_decoder_avg_list, 
                                    gat_decoder_avg_list, 
                                    gformer_decoder_avg_list, 
                                    mixhop_decoder_avg_list, 
                                    gin_decoder_avg_list,
                                    webgnn_decoder_avg_list):
        colors = sns.color_palette("Set2", 6)
        labels = ['NCI ALMANAC', 'O\'NEIL']
        x = np.arange(len(labels))
        width = 0.1
        print(gcn_decoder_avg_list)
        print(gat_decoder_avg_list)
        print(gformer_decoder_avg_list)
        print(mixhop_decoder_avg_list)
        print(gin_decoder_avg_list)
        print(webgnn_decoder_avg_list)
        sns.set_style(style=None)
        gcn = plt.bar(x - 2.5*width, gcn_decoder_avg_list, width, label='GCN Decoder', color=colors[0])
        gat = plt.bar(x - 1.5*width, gat_decoder_avg_list, width, label='GAT Decoder', color=colors[1])
        gformer = plt.bar(x - 0.5*width, gformer_decoder_avg_list, width, label='GraphFormer Decoder', color=colors[2])
        mixhop = plt.bar(x + 0.5*width, mixhop_decoder_avg_list, width, label='MixHop Decoder', color=colors[3])
        gin = plt.bar(x + 1.5*width, gin_decoder_avg_list, width, label='GIN Decoder', color=colors[4])
        webgnn = plt.bar(x + 2.5*width, webgnn_decoder_avg_list, width, label='M3NetFlow', color=colors[5])
        plt.ylabel('Pearson Correlation')
        # plt.title('Pearson Correlation Comparison For 3 GNN Models')
        plt.ylim(0.0, 1.0)
        plt.xticks(x, labels=labels)
        plt.legend(loc='upper right', ncol=2)
        plt.savefig('./data-nci/result/dataset_avg_comparisons.png', dpi=600)
        plt.savefig('./data-oneil/result/dataset_avg_comparisons.png', dpi=600)
        # plt.show()

def model_result(dataset, modelname, epoch_num, rebuild=True):
    model_test_result_list = []
    for fold_n in np.arange(1, 6):
        fold_num = str(fold_n) + 'th'
        if fold_n == 1:
            epoch_name = 'epoch_' + str(epoch_num)
        else:
            epoch_name = 'epoch_' + str(epoch_num) + '_' + str(fold_n-1)
        if os.path.exists('./' + dataset + '/plot') == False:
            os.mkdir('./' + dataset + '/plot')
        # REBUILD BEST ID
        if rebuild == True:
            path = './' + dataset + '/result/' + modelname + '/' + epoch_name
            max_test_id = RebuildLoss().rebuild_loss_pearson(path, epoch_num)
        train_path = './' + dataset + '/result/' + modelname + '/' + epoch_name + '/BestTrainingPred.txt'
        test_path = './' + dataset + '/result/' + modelname + '/' + epoch_name + '/BestTestPred.txt'
        train_pearson, test_pearson = AnalyseCorr().pred_result(fold_n=fold_n, epoch_name=epoch_name, dataset=dataset, modelname=modelname)
        model_test_result_list.append(test_pearson)
    average_test_result = sum(model_test_result_list) / len(model_test_result_list)
    model_test_result_list.append(average_test_result)
    print(model_test_result_list)
    return model_test_result_list

def train_test_split(num_fold=5, dataset='datainfo-nci'):
    for fold_n in range(1, num_fold + 1):
        filtered_data_path = './' + dataset + '/filtered_data'
        train_df_list = []
        for i in range(1, num_fold + 1):
            print(i)
            if i == fold_n:
                print('--- LOADING ' + str(i) + '-TH SPLIT TEST DATA ---')
                test_df = pd.read_csv(filtered_data_path + '/split_input_' + str(i) + '.csv')
            else:
                print('--- LOADING ' + str(i) + '-TH SPLIT TRAINING DATA ---')
                train_df = pd.read_csv(filtered_data_path + '/split_input_' + str(i) + '.csv')
                train_df_list.append(train_df)
        concat_train_df = pd.concat(train_df_list)
        test_df.to_csv(filtered_data_path + '/split_test_input_' + str(fold_n) + '.csv', index=False, header=True)
        concat_train_df.to_csv(filtered_data_path + '/split_train_input_' + str(fold_n) + '.csv', index=False, header=True)
        print(test_df.shape)
        print(concat_train_df.shape)


def build_cell_line_cancer_map(dataset):
    # [cell_line_counts]
    final_dl_input_df = pd.read_csv('./' + dataset + '/filtered_data/final_dl_input.csv')
    value_counts_series = final_dl_input_df['Cell Line Name'].value_counts()
    value_counts_df = value_counts_series.reset_index()
    value_counts_df.columns = ['Cell Line Name', 'Counts']
    value_counts_df = value_counts_df.sort_values(by='Cell Line Name', ascending=True).reset_index(drop=True)
    value_counts_df.to_csv('./' + dataset + '/filtered_data/cell_line_counts.csv', index=False, header=True)
    # [cell_line_cancer_name_map_dict]
    cell_line_cancer_map_df = pd.read_csv('./' + dataset + '/filtered_data/cell_line_cancer_map.csv')
    cell_line_cancer_map_df['Panel Name'] = cell_line_cancer_map_df['Panel Name'].replace('Non-Small Cell Lung', 'Lung')
    cell_line_cancer_name_map_dict_df = pd.merge(value_counts_df, cell_line_cancer_map_df, on='Cell Line Name')
    cell_line_cancer_name_map_dict_df = cell_line_cancer_name_map_dict_df.drop(columns=['Counts', 'Doubling Time', 'Inoculation Density'])
    cell_line_cancer_name_map_dict_df.rename(columns={'Panel Name': 'Cancer_name', 'Cell Line Name': 'Cell_Line_Name'}, inplace=True)
    cell_line_cancer_name_map_dict_df['Cell_Line_Num'] = list(np.arange(1, len(cell_line_cancer_name_map_dict_df['Cancer_name']) + 1))
    cell_line_cancer_name_map_dict_df = cell_line_cancer_name_map_dict_df[['Cell_Line_Name', 'Cell_Line_Num', 'Cancer_name']]
    cell_line_cancer_name_map_dict_df.to_csv('./' + dataset + '/filtered_data/cell_line_cancer_name_map_dict.csv', index=False, header=True)
    print(cell_line_cancer_name_map_dict_df)


def cell_line_cancer_percentage(dataset):
    final_dl_input_df = pd.read_csv('./' + dataset + '/filtered_data/final_dl_input.csv')
    cell_line_cancer_name_map_dict_df = pd.read_csv('./' + dataset + '/filtered_data/cell_line_cancer_name_map_dict.csv')
    final_dl_input_cancer_df = pd.merge(final_dl_input_df, cell_line_cancer_name_map_dict_df, left_on='Cell Line Name', right_on='Cell_Line_Name')
    print(final_dl_input_cancer_df)

    # MAP EACH CELL LINE TO ITS CANCER TYPE
    cell_line_cancer_dict = dict(map(lambda i, j : (i, j) , cell_line_cancer_name_map_dict_df.Cell_Line_Name, cell_line_cancer_name_map_dict_df.Cancer_name))
    # ASSIGN A COLOR FOR EACH CANCER TYPE
    # color_list = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3', '#bcbd22']
    color_list = plt.cm.tab20(np.linspace(0, 1, len(list(set(list(cell_line_cancer_dict.values()))))))
    cancer_to_color_dict = dict(map(lambda i, j : (i, j) , list(set(list(cell_line_cancer_dict.values()))), color_list))

    # HORIZONTAL BAR PLOT
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    ax1.barh(final_dl_input_df['Cell Line Name'].value_counts().index, 
            final_dl_input_df['Cell Line Name'].value_counts().values, 
            color=[cancer_to_color_dict[cell_line_cancer_dict[cell]] for cell in final_dl_input_df['Cell Line Name'].value_counts().index])
    ax1.set_xlabel('Count')
    ax1.set_ylabel('Cell Line')
    ax1.set_title('Count of Cell Lines')
    plt.tight_layout()
    ax1.invert_yaxis()

    # PIE CHART FOR CANCER TYPES
    cancer_type_percentages = final_dl_input_cancer_df['Cancer_name'].value_counts(normalize=True) * 100
    colors = [cancer_to_color_dict[cancer] for cancer in cancer_type_percentages.index]
    plt.figure(figsize=(15, 9))
    cancer_type_percentages.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'fontsize': 14})
    ax2.set_title('Percentage of Cancer Types')
    ax2.set_ylabel('')
    plt.show()

def cell_line_cancer_percentage_split(dataset):
    final_dl_input_df = pd.read_csv('./' + dataset + '/filtered_data/final_dl_input.csv')
    cell_line_cancer_name_map_dict_df = pd.read_csv('./' + dataset + '/filtered_data/cell_line_cancer_name_map_dict.csv')
    final_dl_input_cancer_df = pd.merge(final_dl_input_df, cell_line_cancer_name_map_dict_df, left_on='Cell Line Name', right_on='Cell_Line_Name')
    print(final_dl_input_cancer_df)

    # MAP EACH CELL LINE TO ITS CANCER TYPE
    cell_line_cancer_dict = dict(map(lambda i, j : (i, j) , cell_line_cancer_name_map_dict_df.Cell_Line_Name, cell_line_cancer_name_map_dict_df.Cancer_name))
    # ASSIGN A COLOR FOR EACH CANCER TYPE
    color_list = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3', '#bcbd22']
    # color_list = plt.cm.tab10(np.linspace(0, 1, len(list(set(list(cell_line_cancer_dict.values()))))))
    cancer_to_color_dict = dict(map(lambda i, j : (i, j) , list(set(list(cell_line_cancer_dict.values()))), color_list))

    # HORIZONTAL BAR PLOT
    fig1, ax1 = plt.subplots(figsize=(12, 15))
    colors_bar = [cancer_to_color_dict[cell_line_cancer_dict[cell]] for cell in final_dl_input_df['Cell Line Name'].value_counts().index]
    ax1.barh(final_dl_input_df['Cell Line Name'].value_counts().index, 
            final_dl_input_df['Cell Line Name'].value_counts().values, 
            color=colors_bar)
    ax1.set_xlabel('Count')
    ax1.set_ylabel('Cell Line')
    ax1.set_title('Count of Cell Lines')
    ax1.invert_yaxis()
    plt.tight_layout()
    plt.savefig('./' + dataset + '/result/cell_line_barplot.png', dpi=600)
    # plt.show()  # This will display the first plot


    # PIE CHART FOR CANCER TYPES
    fig2, ax2 = plt.subplots(figsize=(15, 9))
    cancer_type_percentages = final_dl_input_cancer_df['Cancer_name'].value_counts(normalize=True) * 100
    colors_pie = [cancer_to_color_dict[cancer] for cancer in cancer_type_percentages.index]
    cancer_type_percentages.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=140, colors=colors_pie, textprops={'fontsize': 18})
    ax2.set_title('Percentage of Cancer Types')
    ax2.set_ylabel('')
    plt.savefig('./' + dataset + '/result/cancer_cell_line_pieplot.png', dpi=600)
    # plt.show()  # This will display the second plot


# Custom function to rotate the labels
def func(pct, allvalues): 
    absolute = int(pct / 100.*np.sum(allvalues)) 
    return "{:.1f}%\n".format(pct, absolute)


if __name__ == "__main__":
    ### DATASET SELECTION
    dataset = 'data-nci'
    # dataset = 'data-oneil'
    # rebuild = True
    rebuild = False

    # ### MODEL SELECTION
    # if dataset == 'data-nci':
    #     gcn_decoder_test_list = model_result(dataset=dataset, modelname='gcn', epoch_num=100, rebuild=rebuild)
    #     gat_decoder_test_list = model_result(dataset=dataset, modelname='gat', epoch_num=100, rebuild=rebuild)
    #     gformer_decoder_test_list = model_result(dataset=dataset, modelname='gformer', epoch_num=200, rebuild=rebuild)
    #     mixhop_decoder_test_list = model_result(dataset=dataset, modelname='mixhop', epoch_num=200, rebuild=rebuild)
    #     gin_decoder_test_list = model_result(dataset=dataset, modelname='gin', epoch_num=200, rebuild=rebuild)
    #     webgnn_decoder_test_list = model_result(dataset=dataset, modelname='webgnn', epoch_num=500, rebuild=rebuild)
    # elif dataset == 'data-oneil':
    #     gcn_decoder_test_list = model_result(dataset=dataset, modelname='gcn', epoch_num=100, rebuild=rebuild)
    #     gat_decoder_test_list = model_result(dataset=dataset, modelname='gat', epoch_num=100, rebuild=rebuild) 
    #     gformer_decoder_test_list = model_result(dataset=dataset, modelname='gformer', epoch_num=100, rebuild=rebuild)
    #     mixhop_decoder_test_list = model_result(dataset=dataset, modelname='mixhop', epoch_num=100, rebuild=rebuild)
    #     gin_decoder_test_list = model_result(dataset=dataset, modelname='gin', epoch_num=100, rebuild=rebuild)
    #     webgnn_decoder_test_list = model_result(dataset=dataset, modelname='webgnn', epoch_num=100, rebuild=rebuild)

    # ### NCI-ALMANAC
    # gcn_decoder_test_list = [0.4130003816635538, 0.4662483372799231, 0.5370335322761259, 0.4194793977603401, 0.40824100173344124, 0.44880053014267685]
    # gat_decoder_test_list = [0.26376485906231467, 0.2848270231318383, 0.13984699396293215, 0.10261948454381241, 0.22744885730348186, 0.20370144360087586]
    # gformer_decoder_test_list = [0.3401364920237653, 0.450464128651303, 0.3210135831806914, 0.3603290521749046, 0.34775804415504713, 0.3639402600371423]
    # mixhop_decoder_test_list = [0.5543345142484409, 0.553354672766029, 0.5530773338442082, 0.551463043350704, 0.19403301031027562, 0.4812525149039315]
    # gin_decoder_test_list = [0.5346631585350167, 0.5355933804574946, 0.6135699971683238, 0.5148608612661582, 0.44817324371648787, 0.5293721282286963]
    # webgnn_decoder_test_list = [0.6397148600951211, 0.62665668248812, 0.6550570523219267, 0.6529237122532979, 0.6132623125813826, 0.6375229239479697]

    # ### O'NEIL
    # gcn_decoder_test_list = [0.41033774433685655, 0.41238576688957074, 0.5197152727755879, 0.6265475866754472, 0.5342658587375002, 0.5006504458829926]
    # gat_decoder_test_list = [0.47572474192387526, 0.06893487590156398, 0.44111973137933025, 0.21029094901113685, 0.3811419810883614, 0.31544245586085357]
    # gformer_decoder_test_list = [0.2713893427081094, 0.21219459595575807, 0.42128108095074707, 0.45728565163651524, 0.07074770191061115, 0.2865796746323482]
    # mixhop_decoder_test_list = [0.0772987028887031, 0.07128515265480145, 0.1551026748912726, 0.04272932358065324, 0.0002577887499931987, 0.06933472855308473]
    # gin_decoder_test_list = [0.18812599794165918, 0.1733832212389168, 0.2460039719862855, 0.40974219670524653, 0.1497926428982809, 0.2334096061540778]
    # webgnn_decoder_test_list = [0.6710612105275339, 0.6219820023140109, 0.6265848478536921, 0.6903138630310607, 0.6807606739300186, 0.6581405195312632]

    ### DATASET SCORES
    gcn_decoder_avg_list = [0.44880053014267685, 0.5006504458829926]
    gat_decoder_avg_list = [0.20370144360087586, 0.31544245586085357]
    gformer_decoder_avg_list = [0.3639402600371423, 0.2865796746323482]
    mixhop_decoder_avg_list = [0.4812525149039315, 0.06933472855308473]
    gin_decoder_avg_list = [0.5293721282286963, 0.2334096061540778]
    webgnn_decoder_avg_list = [0.6375229239479697, 0.6581405195312632]

    # AnalyseCorr().fold_comparison(dataset, gcn_decoder_test_list, 
    #                                 gat_decoder_test_list, 
    #                                 webgnn_decoder_test_list, 
    #                                 gformer_decoder_test_list, 
    #                                 mixhop_decoder_test_list, 
    #                                 gin_decoder_test_list)
    

    AnalyseCorr().dataset_avg_comparison(dataset, gcn_decoder_avg_list, 
                                    gat_decoder_avg_list, 
                                    gformer_decoder_avg_list, 
                                    mixhop_decoder_avg_list, 
                                    gin_decoder_avg_list,
                                    webgnn_decoder_avg_list)


    # AnalyseCorr().pred_result(fold_n=1, epoch_name='epoch_100', dataset=dataset, modelname='tsgnn')
    # AnalyseCorr().pred_all_result(num_fold=5, epoch_num=100, dataset=dataset, modelname='tsgnn', train_mean=False)


    # build_cell_line_cancer_map(dataset=dataset)
    # cell_line_cancer_percentage(dataset=dataset)
    # cell_line_cancer_percentage_split(dataset=dataset)