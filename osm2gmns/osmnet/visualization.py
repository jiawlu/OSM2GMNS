def _draw(network, figsize):
    import matplotlib.pyplot as plt
    import numpy as np

    xy_list = []
    for node_id, node in network.node_dict.items():
        xy = list(node.geometry_xy.coords)[0]
        xy_list.append(xy)
    xy_array = np.array(xy_list)

    if figsize is None:
        net_length = xy_array[:,0].max() - xy_array[:,0].min()
        net_width = xy_array[:,1].max() - xy_array[:,1].min()
        fig_length = 16
        fig_width = fig_length / net_length * net_width
        plt.figure(figsize=(fig_length, fig_width))
    else:
        plt.figure(figsize=figsize)

    ax = plt.gca()
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    plt.scatter(xy_array[:, 0], xy_array[:, 1], s=16.0, color='darkorange', zorder=1)

    for link_id, link in network.link_dict.items():
        xys = list(link.geometry_xy.coords)
        xys_array = np.array(xys)
        plt.plot(xys_array[:,0], xys_array[:,1], linewidth=1, color='deepskyblue', zorder=0)


def show(network, save=False, figsize=None):
    """
    Show the network in a pop-up window

    Parameters
    ----------
    network: Network
        an osm2gmns Network object
    save: bool
        if True, the plot will also be saved to a local file named network.jpg
    figsize: tuple of int/float, list of int/float
        size of the figure

    Returns
    -------
    None
    """
    if network.number_of_nodes == 0:
        print('WARNING: Cannot show an empty network')
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("Matplotlib is required to show the network") from e

    _draw(network, figsize)
    if save:
        plt.savefig('network.jpg')
        print(f'Figure is saved to network.jpg')

    plt.show()
    plt.close()


def saveFig(network, picpath='network.jpg',figsize=None):
    """
    Save the network plot to a local file

    Parameters
    ----------
    network: Network
        an osm2gmns Network object
    picpath: str
        path to store to network plot. can be an absolute or a relative path
    figsize: tuple of int/float, list of int/float
        size of the figure

    Returns
    -------
    None
    """

    if network.number_of_nodes == 0:
        print('WARNING: Cannot show an empty network')
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError("Matplotlib is required to show the network") from e

    _draw(network, figsize)
    plt.savefig(picpath)
    plt.close()
    print(f'Figure is saved to {picpath}')
