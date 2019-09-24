"""
A module consisting of pipeline steps that processed events will pass through.
"""

from abc import ABC, abstractmethod
from collections import deque, namedtuple
import logging
from time import time

class AveragedEvent():
    def __init__(self, average_event):
        self.location_id = average_event[0]
        self.value = average_event[1]
        self.timestamp = average_event[2]

    def __str__(self):
        return f"location_id={self.location_id}, value={self.value}, timestamp={self.timestamp}"


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

    def __init__(self, run_time_seconds):
        """
        Create a FixedDurationSource which will run for the given duration.
        """
        self.run_time_seconds = run_time_seconds
        self.events_processed = 0

    def handle(self, events):
        """
        Pass on all events from the source, but cut it off when the time limit is reached.
        """

        # Calculate the time at which we should stop processing
        end_time = time() + self.run_time_seconds
        logger.info(f'Processing events for {self.run_time_seconds} seconds')
        start_time = time()

        ids_set = set()
        loc_set = set()

        # Process events for as long as we still have time remaining
        i=0
        recent_events = []
        for event in events:
            if time() < end_time:
                if event.event_id in ids_set:
                    i=i+1
                    continue
                else:
                    recent_events.append(event)
                    ids_set.add(event.event_id)
                    loc_set.add(event.location_id)
                    if time() - start_time > 30:
                        print("Run for longer than 30 seconds")
                        print("Most recent event is:")
                        print(event, event.location_id)
                        for id in loc_set:
                            print("Location ID is")
                            print(id)
                            values = []
                            times = []
                            for recent_event in recent_events:
                                if id in recent_event:
                                    print(recent_event)
                                    values.append(float(recent_event.value))
                                    times.append(int(recent_event.timestamp))
                            values_average = float(sum(values)) / float(len(values))
                            times_average = float(sum(times)) / float(len(times))
                            times_average = int(round(times_average))
                            loc_average_event = AveragedEvent(average_event=[id,values_average,times_average])
                            print("Averaged location event is")
                            print(loc_average_event)
                            logger.debug(f'Procesing event: {loc_average_event}')
                            i=i+1
                            self.events_processed += 1
                            yield loc_average_event

                        start_time = time()
                    logger.debug(f'Procesing event: {event}')
                    self.events_processed += 1
                    i=i+1
                    yield event
            else:
                logger.info('Finished processing events')
                print(len(ids_set))
                print(i)
                return