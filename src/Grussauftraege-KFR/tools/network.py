from os import makedirs
import sys
from os.path import abspath, dirname, join
from typing import Union, Optional, Literal
from math import sqrt

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

BASE_PATH = abspath(__file__)
ROOT_PATH = dirname(dirname(dirname(dirname(BASE_PATH))))
IMAGE_PATH = join(ROOT_PATH, 'network_diagram')
SAVE_PATH = join(ROOT_PATH, 'network_degree')


def generate_triples_dataframe(df: pd.DataFrame, subject: Union[str, list[str]], object: Union[str, list[str]],
                               use_same_place: Literal[True, False],
                               illocution: Optional[Union[str, list[str]]] = None, time_span: Optional[str] = None
                               ) -> pd.DataFrame:
    """
    Generate a DataFrame of triples from the given DataFrame.
    Parameters:
        df (pd.DataFrame): The DataFrame containing correspondence data.
        subject (Union[str, list[str]]): The subject(s) to filter by.
        object (Union[str, list[str]]): The object(s) to filter by.
        use_same_place (Literal[True, False]): If True, filter by letters sent and received at the same place.
        illocution (Optional[str]): The illocution to filter by, if any.
        time_span (Optional[str]): A time span in the format 'start_date,end_date' to filter by letter dates.
    Returns:
        pd.DataFrame: A DataFrame containing triples of subject, predicate, and object.
    """
    if isinstance(subject, str):
        subject = [subject]
    if isinstance(object, str):
        object = [object]
    target_df = df[(df['subject_name'].isin(subject))|(df['object_name'].isin(subject))]

    if illocution:
        if isinstance(illocution, str):
            illocution = [illocution]  
        target_illocution_df = target_df[target_df['illocution'].isin(illocution)]
    else:
        target_illocution_df = target_df

    if time_span:
        start_date, end_date = time_span.split(',')
        target_date_df = target_illocution_df[target_illocution_df['letter_date'].between(start_date.strip(), end_date.strip())]
    else:
        target_date_df = target_illocution_df

    if use_same_place == True:
        target_place_df = target_date_df.loc[target_date_df['dispatch'] == target_date_df['receipt']]
        places = target_place_df['dispatch'].unique()
        for place in places:
            target_df = target_place_df.loc[target_place_df['dispatch'] == place]
            target_df = target_df[['subject_name','object_name']]
            target_df = target_df.groupby(['subject_name']).value_counts()
            target_df = target_df.reset_index()
            target_df['weight'] = [c/10 for c in target_df['count']]
            if time_span:
                target_df.to_csv(join(SAVE_PATH, f'{str(*illocution)}_{time_span}_{place}_triples - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.csv'), sep=';',
                                 index=False, encoding='utf-8')
            else:
                target_df.to_csv(join(SAVE_PATH, f'{str(*illocution)}_{place}_triples - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.csv'), sep=';',
                                 index=False, encoding='utf-8')
    else:
        target_df = target_date_df[['subject_name','object_name']]
        target_df = target_df.groupby(['subject_name']).value_counts()
        target_df = target_df.reset_index()
        target_df['weight'] = [c/10 for c in target_df['count']]
    return target_df


def generate_triples_network_graph(target_df: pd.DataFrame, illocution: str,
                                   time_span: Optional[str], same_place: Optional[str],
                                   k: int, figsize: tuple, use_curved_edges: Literal[True, False], use_count: Literal[True, False],
                                   filter: Optional[int]=None) -> nx.Graph:
    """
    Generate a network graph from the given DataFrame of triples.
    Parameters:
        target_df (pd.DataFrame): The DataFrame containing triples of subject, predicate, and object.
        illocution (str): The illocution to be displayed in the graph title.
        time_span (Optional[str]): A time span in the format 'start_date and end_date' to be displayed in the graph title.
        same_place (Optional[str]): A place to be displayed in the graph title.
        k (int): The spring layout parameter for the graph.
        figsize (tuple): The size of the figure for the graph.
        use_curved_edges (Literal[True, False]): If True, generate a network with curved edges; if False, generate an network with straight edges.
        use_count (Literal[True, False]): If True, edges are weighted by count; if False, edges are weighted by weight (= count/10).
        filter (Optional[int]): A threshold for filtering edges by count.
    Returns:
        nx.Graph: A NetworkX graph object representing the network of triples.
    """
    if filter:
        target_df = target_df[target_df['count'] > filter]
    else:
        target_df = target_df
    g = nx.from_pandas_edgelist(target_df,
                                source='subject_name',
                                target='object_name',
                                edge_attr=True,
                                create_using=nx.MultiDiGraph()
                                )
    if use_count == False:
        weights = nx.get_edge_attributes(g, 'weight').values()
    else:
        weights = nx.get_edge_attributes(g, 'count').values()
    in_degrees = dict(g.in_degree())
    
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    plt.axis('off')
    plt.tight_layout()
    pos = nx.spring_layout(g, k=k/sqrt(g.order()))
    nx.draw_networkx_nodes(g, pos, node_size=[v*100 for v in in_degrees.values()], node_color=in_degrees.values(), alpha=0.7, cmap=plt.cm.viridis)
    if use_curved_edges == True:
        nx.draw_networkx_edges(g, pos, width=list(weights), arrows=True,
                               arrowsize=7, arrowstyle='-|>', connectionstyle='arc3, rad=0.1', alpha=0.7)
    else:
        nx.draw_networkx_edges(g, pos, width=list(weights), arrows=True,
                               arrowsize=7, arrowstyle='-|>', connectionstyle='arc3', alpha=0.7)
    nx.draw_networkx_labels(g, pos, font_family='sans-serif', font_color='black', font_size=7, font_weight='normal')
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=min(in_degrees.values()), vmax=max(in_degrees.values())))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('In-Degree', rotation=270, labelpad=15)
    makedirs(IMAGE_PATH, exist_ok=True)
    if time_span:
        time_span = time_span.replace(', ', ' and ')
        if same_place:
            if filter:
                plt.title(f'Network of Illocution \'{illocution}\' between {time_span} in {same_place} without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' between {time_span} in {same_place} without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'Network of Illocution \'{illocution}\' between {time_span} in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' between {time_span} in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight') 
        else:
            if filter:
                plt.title(f'Network of Illocution \'{illocution}\' between {time_span} without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' between {time_span} without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'Network of Illocution \'{illocution}\' between {time_span} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' between {time_span} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
    else:
        if same_place:
            if filter:
                plt.title(f'Network of Illocution \'{illocution}\' in {same_place} without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' in {same_place} without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'Network of Illocution \'{illocution}\' in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
        else:
            if filter:
                plt.title(f'Network of Illocution \'{illocution}\' without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' without weight {filter} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'Network of Illocution \'{illocution}\' - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Network of Illocution \'{illocution}\' - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
    
    plt.show()
    plt.close()
    return g


def generate_in_out_degree_network(g: nx.Graph, illocution: str,
                                   time_span: Optional[str], same_place: Optional[str],
                                   k: int, figsize: tuple, use_in_degree: Literal[True, False],
                                   use_curved_edges: Literal[True, False], use_count: Literal[True, False]) -> nx.Graph:
    """
    Generate a network graph showing the in-degree or out-degree of nodes in the given graph.
    Parameters:
        g (nx.Graph): The input graph from which to generate the in-degree or out-degree network.
        illocution (str): The illocution to be displayed in the graph title.
        time_span (Optional[str]): A time span in the format 'start_date and end_date' to be displayed in the graph title.
        same_place (Optional[str]): A place to be displayed in the graph title.
        k (int): The spring layout parameter for the graph.
        figsize (tuple): The size of the figure for the graph.
        use_in_degree (bool): If True, generate an in-degree network; if False, generate an out-degree network.
        use_curved_edges (Literal[True, False]): If True, generate a network with curved edges; if False, generate an network with straight edges.
        use_count (Literal[True, False]): If True, edges are weighted by count; if False, edges are weighted by weight (= count/10).
    Returns:
        nx.Graph: The generated in-degree or out-degree network graph.
    """
    while True:
        prev = len(g.nodes())
        if use_in_degree:
            ex_degrees = dict(g.in_degree())
        else:
            ex_degrees = dict(g.out_degree())
        nodes_to_be_removed = [n for n, v in ex_degrees.items() if v < 1]
        g.remove_nodes_from(nodes_to_be_removed)
        next = len(g.nodes())
        if prev == next:
            break

    if use_in_degree:
        degrees = dict(g.in_degree())
        label = 'In-Degree'
    else:
        degrees = dict(g.out_degree())
        label = 'Out-Degree'
    if use_count == False:
        weights = nx.get_edge_attributes(g, 'weight').values()
    else:
        weights = nx.get_edge_attributes(g, 'count').values()
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    plt.axis('off')
    plt.tight_layout()
    pos = nx.spring_layout(g, k=k/sqrt(g.order()))
    nx.draw_networkx_nodes(g, pos, node_size=[v*100 for v in degrees.values()], node_color=degrees.values(), alpha=0.7, cmap=plt.cm.viridis)
    if use_curved_edges == True:
        nx.draw_networkx_edges(g, pos, width=list(weights), arrows=True,
                               arrowsize=7, arrowstyle='-|>', connectionstyle='arc3, rad=0.1', alpha=0.7)
    else:
        nx.draw_networkx_edges(g, pos, width=list(weights), arrows=True,
                               arrowsize=7, arrowstyle='-|>', connectionstyle='arc3', alpha=0.7)
    nx.draw_networkx_labels(g, pos, font_family='sans-serif', font_color='black', font_size=7, font_weight='normal')
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=min(degrees.values()), vmax=max(degrees.values())))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label(label, rotation=270, labelpad=15)
    makedirs(IMAGE_PATH, exist_ok=True)
    if use_in_degree:
        if time_span:
            time_span = time_span.replace(', ', ' and ')
            if same_place:
                plt.title(f'In-Degree Network of Illocution \'{illocution}\' between {time_span} in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'In-Degree Network of Illocution \'{illocution}\' between {time_span} in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'In-Degree Network of Illocution \'{illocution}\' between {time_span} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'In-Degree Network of Illocution \'{illocution}\' between {time_span} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
        else:
            if same_place:
                plt.title(f'In-Degree Network of Illocution \'{illocution}\' in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'In-Degree Network of Illocution \'{illocution}\' in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'In-Degree Network of Illocution \'{illocution}\' - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'In-Degree Network of Illocution \'{illocution}\' - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
    else:
        if time_span:
            time_span = time_span.replace(', ', ' and ')
            if same_place:
                plt.title(f'Out-Degree Network of Illocution \'{illocution}\' between {time_span} in {same_place}')
                plt.savefig(join(IMAGE_PATH, f'Out-Degree Network of Illocution \'{illocution}\' between {time_span} in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'Out-Degree Network of Illocution \'{illocution}\' between {time_span} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Out-Degree Network of Illocution \'{illocution}\' between {time_span} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
        else:
            if same_place:
                plt.title(f'Out-Degree Network of Illocution \'{illocution}\' in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Out-Degree Network of Illocution \'{illocution}\' in {same_place} - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
            else:
                plt.title(f'Out-Degree Network of Illocution \'{illocution}\' - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels')
                plt.savefig(join(IMAGE_PATH, f'Out-Degree Network of Illocution \'{illocution}\' - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.png'), bbox_inches='tight')
    plt.show()
    plt.close()
    return g


def calculate_in_out_degree(df: pd.DataFrame, illocution: str) -> pd.DataFrame:
    """
    Generate a network graph showing the in-degree or out-degree of nodes in the given graph.
    Parameters:
        df (pd.DataFrame): The input DataFrame containing the network data.
        illocution (str): The illocution to be displayed in the graph title.
    Returns:
        pd.DataFrame: A DataFrame containing the in-degree and out-degree information.
    """
    g = nx.from_pandas_edgelist(df,
                                source='subject_name',
                                target='object_name',
                                edge_attr=True,
                                create_using=nx.MultiDiGraph()
                                )
    nodes = list(dict(g.degree()).keys())
    in_degrees = list(dict(g.in_degree()).values())
    out_degrees = list(dict(g.out_degree()).values())
    data = pd.DataFrame({'Node':nodes, 'In-Degree':in_degrees, 'Out-Degree':out_degrees})
    data.to_csv(join(SAVE_PATH, f'{illocution}_in_out_degree - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.csv'), sep=';',
                index=False, encoding='utf-8')
    print(f"The csv file \'{illocution}_in_out_degree - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels.csv\' has been created at {SAVE_PATH}.")
    print(f"The data frame is organized into {data.shape[0]} rows and {data.shape[1]} columns.")
       