3D Wireframe Plots With Matplotlib
==================================

::

    from mpl_toolkits.mplot3d import axes3d
    import matplotlib.pyplot as plt
    import numpy 
    
    



.. currentmodule:: mpl_toolkits
.. autosummary::
   :toctree: api

   mplot3d
   mplot3d.axes3d
   mplot3d.axes3d.get_test_data
   axes3d.plot_wireframe
   axes3d.plot_surface

::

    output = 'figures/wiredframe_1.svg'
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    #ax = fig.add_subplot(projection='3d')
    X, Y, Z = axes3d.get_test_data(0.05)
    ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
    #>plt.show()
    fig.savefig(output)
    
    

.. figure:: figures/wiredframe_1.svg



.. currentmodule:: numpy
.. autosummary::
   :toctree: api

   arange
   meshgrid
   
::

    output = 'figures/trig_plot.svg'
    figure = plt.figure()
    axe = figure.gca(projection='3d')
    X = numpy.arange(-5, 5, 0.25)
    Y = numpy.arange(-5, 5, 0.25)
    X, Y = numpy.meshgrid(X, Y)
    radius = numpy.sqrt(X**2 + Y**2)
    Z = numpy.sin(radius)
    surface = axe.plot_surface(X, Y, Z, rstride=1, cstride=1)
    axe.set_zlim(-1.01, 1.01)
    #axe.zaxis.set_major_
    figure.savefig(output)
    
    

.. figure:: figures/trig_plot.svg

