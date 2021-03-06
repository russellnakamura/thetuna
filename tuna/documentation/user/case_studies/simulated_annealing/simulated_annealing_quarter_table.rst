Simulated Annealing With Simulated (Quarter) Table Data
=======================================================



Problem
-------

*How can we understand how the `Simulated Annealing` parameters should be set while trying to optimize device placement on a table?*

This continues the :ref:`Simulated Annealing with Simulated Table Data <case-study-annealing-simulated-table>` problem. Since the best data-point was in the top-left corner and the data-points with 70 Mbits/second were on the left-half of the table I'll see what happens when we only search the top-left corner.

.. '

The Simulation Data
-------------------

::

    data_path = '../data/data_step50.csv'
    z_data_full = numpy.loadtxt(data_path, delimiter=',')
    z_data = z_data_full[0:30, 30:60]
    
    



When I plotted the scatter plots earlier they were rotated so that they matched the contour map. To figure out what the indices will be for the corner we want in the data-matrix, it'll be easier if we flip the x and y axes back so that the x-axis becomes the columns and the y-axis becomes the rows.

.. '

.. figure:: figures/full_table_scatter.png
   :scale: 75%

   Max-throughput (72.7 Mb/s) at (2550, 350) indicated by intersection of red lines.
   Min-throughput (0.22 Mb/s) at (2950, 1200) indicated by intersection of blue lines.

.. figure:: figures/quarter_table_scatter.png
   :scale: 75%

   Max-throughput (72.7 Mb/s) at (1050, 350) indicated by intersection of red lines.
   Min-throughput (0.22 Mb/s) at (1450, 1200) indicated by intersection of blue lines.




Sample Configuration File
-------------------------

In this case the only real difference are the limits set and the removal of the candidate Solution.

.. literalinclude:: data/tuna_quarter_table_settings.ini

TUNA Section
~~~~~~~~~~~~

The ``[TUNA]`` section is a place to list what the plugin sections will be. In this case we're telling the `tuna` that there will only be one plugin and the information to configure it will be in a section named ``[Annealing]``.

DEFAULT Section
~~~~~~~~~~~~~~~

We're going to repeat the simulation 1000 times and store the data in a folder named `annealing_tabledata_t0_10000_scale_2_quarter_table` next to the configuration file.

MODULES Section
~~~~~~~~~~~~~~~

We're simulating the use of Cameron's XYTable so we need to tell the `tuna` which module contains the plugin to fake the table's operation.

.. '

Annealing Section
~~~~~~~~~~~~~~~~~

The ``plugin = SimulatedAnnealing`` line tells the tuna to load the `SimulatedAnnealing` class. 

The ``components = fake_table, table_data`` line tells the tuna to create components using the `fake_table` and `table_data` section in this configuration and give it to the Simulated Annealer (wrapped in a :ref:`composite <simple-composite>`). The components will be used to decide how good a location is.

The ``observers = fake_table`` line tells the `tuna` to give the `Simulated Annealer` a copy of the table-mock so that it will call it once it stops. This simulates moving the table to the best solution found at the end of an optimization run.

The Outcome
-----------

How many times did it find the maximum-bandwidth location?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the `tuna` finds the ideal value (or it exceeds the time limit we set) it outputs "Stop condition reached" along with the coordinates and bandwidth found, which look like this example::

   Stop condition reached with solution: Inputs: [  7.  51.] Output: 72.7

To get the number of cases where 72.7 Mbits/second was found:

.. code-block:: bash

   grep "Stop.*Output:[[:space:]]*72\.7" tuna.log  | wc -l

This gives us 851 out of 1,000.


How many times did it do well enough?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Picking an arbitrary value of 70 Mbits/second as the lower bound of an acceptable bandwidth, how often did the optimizer exceed this lower bound?

.. code-block:: bash

   grep "Quality.*Output:[[:space:]]*7[[:digit:]]" tuna.log  | wc -l

In all cases it reached found a spot with at least 70 Mbits/second.

How well did it typically do?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By diverting the output from the previous `grep` search to a (:download:`file <data/half_table_bandwidths.log>`) instead of piping it to `wc`, I was able to get the final bandwidths the `tuna` reached (it's included in the "Quality Checks" line as "Output:")::

   Quality Checks: 1486 Solution: Inputs: [  7.  51.] Output: 72.7

.. '




.. csv-table:: Bandwidth Solutions Summary
   :header: Statistic, Value

   count,1000.0
   mean,72.5253
   std,0.425571405546
   min,71.0
   25%,72.7
   50%,72.7
   75%,72.7
   max,72.7

.. figure:: figures/quarter_table_bandwidths_kde.png
   :scale: 75%



So in the worst case it did 71.0 Mbits/second, compared to 70.3 for the full table. To get an idea of a reasonable range for the `mean` bandwidth I'll use a 99% confidence interval. Since the data isn't normal I'll use resampling.

.. '

::

    trials = 10**5
    n = bandwidths.shape[0]
    samples = numpy.random.choice(bandwidths.Bandwidth,
                                  size=(n, trials))
    means = samples.mean(axis=0)
    alpha = 0.01
    p = alpha/2
    
    low = numpy.percentile(means, p)
    high = numpy.percentile(means, 1-p)
    
    

**99% Confidence Interval:** (72.4733, 72.4934)



So if we ran the optimizer often enough and the data always looked like our data set then we would expect the mean of the outcomes to be between 72.47 and 72.49 Mbits/Second 99% of the time. So how long did the optimizer take to get to these values?

How long were the execution times?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To estimate the execution times we need to see how many times the Temperature was changed for each search (the temperature changes before each candidate-check). First a subset of the log was created.

.. code-block:: bash

    grep "Initial\|Temperature" tuna.log > initial_temperatures.log

Then I counted the temperature checks between the "Initial" lines.

::

    repetitions = 0
    out_file = "data/quarter_table_best_repetitions_counts.csv"
    if not os.path.isfile(out_file):
        with open(out_file, 'w') as w:
            w.write("TemperatureCount\n")
            for line in open("data/quarter_table_initial_temperatures.log"):
                if "Initial" in line and repetitions !=0:
                    w.write("{0}\n".format(repetitions))
                    repetitions = 0
                    continue
                if "Temperature" in line:
                    repetitions += 1
            w.write("{0}\n".format(repetitions))
    
    

::

    counts = pandas.read_csv(out_file)
    description = counts.TemperatureCount.describe()
    
    



.. csv-table:: Temperature Counts Summary
   :header: Statistic, Value

   count,998
   mean,464.979
   std,251.843
   min,1
   25%,253.25
   50%,468
   75%,689
   max,916



To estimate the running time we have to now pick an arbitrary time for each execution. I'll use 15 seconds on the assumption that the default iperf run-time of 10 seconds is used and it takes 5 seconds to move the table (on average).

.. '

.. math::

   estimate = runtime \times count
   
::

    RUNTIME = 15
    SECONDS_PER_HOUR = 60.0 * 60.0
    
    



.. csv-table:: Estimated Running Times
   :header: Statistic, Running Time (Hours)

   min,0.0042
   50%,1.9
   max,3.8

::

    runtimes = counts.TemperatureCount * RUNTIME/SECONDS_PER_HOUR
    samples = numpy.random.choice(runtimes, size=(runtimes.shape[0], trials))
    means = samples.mean(axis=0)
    medians = numpy.median(samples, axis=0)
    low = numpy.percentile(means, p)
    high = numpy.percentile(means, 1-p)
    
    low_median = numpy.percentile(medians, p)
    high_median = numpy.percentile(medians, 1-p)
    
    

**99% Confidence Interval (mean):** (1.81, 1.86)

**99% Confidence Interval (Median):** (1.78, 1.84)

.. figure:: figures/quarter_table_runtime_kde.png
   :scale: 75%



   Estimated running times for each search based on a 15 second iperf/table-movement time.

So it looks like if we wanted to be very sure we got a high-enough solution we would need to let the Annealer run for about four hours. But on average it takes 1.78 to 1.84 hours. 
