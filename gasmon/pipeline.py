"""
A module consisting of pipeline steps that processed events will pass through.
"""

from abc import ABC, abstractmethod
from collections import deque, namedtuple
import logging
from time import time
from gasmon.locations import Location
from gasmon.plot import plot

class AveragedEvent():
    def __init__(self, average_event):
        self.location_id = average_event[0]
        self.x = average_event[1]
        self.y = average_event[2]
        self.value = average_event[3]
        self.timestamp = average_event[4]

    def __str__(self):
        return f"{self.location_id},{self.x}, {self.y}, {self.value},{self.timestamp},"

class SensorsAverage():
    def __init__(self, sensors_average):
        self.value = sensors_average[0]
        self.timestamp = sensors_average[1]
    def __str__(self):
        return f"{self.value},{self.timestamp},"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Pipeline(ABC):
    """
    An abstract base class for pipeline steps.
    """

    @abstractmethod
    def handle(self, events):
        """
        Transform the given stream of events into a processed stream of events.
        """
        pass

    def sink(self, sink):
        """
        Funnel events from this Pipeline into the given sink.
        """
        return PipelineWithSink(self, sink)


class PipelineWithSink(Pipeline):
    """
    A Pipeline with a final processing step (a Sink).
    """

    def __init__(self, pipeline, sink):
        """
        Create a Pipeline with a Sink.
        """
        self.pipeline = pipeline
        self.sink = sink

    def handle(self, events):
        """
        Handle events by first letting the pipeline process them, then 
        passing the result to the sink
        """
        self.sink.handle(self.pipeline.handle(events))


class FixedDurationSource(Pipeline):
    """
    A Pipeline step that processes events for a fixed duration.
    """

    def __init__(self, run_time_seconds, locations):
        """
        Create a FixedDurationSource which will run for the given duration.
        """
        self.run_time_seconds = run_time_seconds
        self.events_processed = 0
        self.locations = locations

    def handle(self, events):
        """
        Pass on all events from the source, but cut it off when the time limit is reached.
        """

        # Calculate the time at which we should stop processing
        end_time = time() + self.run_time_seconds
        logger.info(f'Processing events for {self.run_time_seconds} seconds')
        start_time = time()
        duration = end_time - start_time
        block_time = 20

        ids_set = set()
        loc_set = set()

        # Process events for as long as we still have time remaining
        i=0
        j=1
        k=1
        recent_events = []
        with open("averaged_readings.csv",'w') as out:
            out.write("Location ID, x, y, Value, Timestamp, Block, Total runtime = "+str(duration)+", Block time = "+str(block_time)+" \n")
        out.close()

        with open("averaged_sensors.csv",'w') as out:
            out.write("Timestamp, Value, Block, Total runtime = "+str(duration)+", Block time = "+str(block_time)+" \n")
        out.close()

        for event in events:
            if time() < end_time:
                if event.event_id in ids_set:
                    i=i+1
                    continue
                else:
                    recent_events.append(event)
                    ids_set.add(event.event_id)
                    loc_set.add(event.location_id)
                    i=i+1
                    if (time() - start_time) > block_time:
                        plot_data = []
                        av_sensor_values = []
                        av_sensor_times = []
                        for id in loc_set:
                            values = []
                            times = []
                            for recent_event in recent_events:
                                if id in recent_event:
                                    values.append(float(recent_event.value))
                                    times.append(int(recent_event.timestamp))
                            values_average = float(sum(values)) / float(len(values))
                            times_average = float(sum(times)) / float(len(times))
                            times_average = int(round(times_average))
                            av_sensor_values.append(values_average)
                            av_sensor_times.append(float(times_average))
                            for Location in self.locations:
                                if id == Location.id:
                                    x = Location.x
                                    y = Location.y
                            loc_average_event = AveragedEvent(average_event=[id, x, y, values_average, times_average])
                            print("Averaged location event is")
                            logger.debug(f'Processing average event: {loc_average_event}')
                            with open("averaged_readings.csv",'a') as out:
                                out.write(f'{loc_average_event}'+str(k)+"\n")
                            out.close()
                            xyz = [x, y, values_average]
                            plot_data.append(xyz)
                            j=j+1
                            yield loc_average_event

                        av_sensor_val = sum(av_sensor_values) / float(len(av_sensor_values))
                        av_sensor_time = sum(av_sensor_times) / float(len(av_sensor_times))
                        av_sensor_time = int(av_sensor_time)
                        all_sensors_average = SensorsAverage(sensors_average=[av_sensor_val,av_sensor_time])
                        with open("averaged_sensors.csv", 'a') as out:
                            out.write(f'{all_sensors_average}' + str(k) + "\n")
                        out.close()
                        plot(plot_data)

                        k=k+1
                        start_time = time()
                        self.events_processed += 1


                    else:
                        logger.debug(f'Procesing event: {event}')
                        self.events_processed += 1
            else:
                logger.info('Finished processing events')
                print("Number of unique events processed")
                print(len(ids_set))
                print("All events including duplicates")
                print(i)
                print("Total number of averaged events")
                print(j)
                return