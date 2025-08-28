# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Observable Mixin class definition."""
from collections import defaultdict
from typing import Any, Callable, DefaultDict, List


class ObservableMixin:
    """
    Mixin to make an object observable.

    An observable object has 3 new methods available on it:
    subscribe, subscribe_all, and notify_topic.
    """

    __slots__ = ["_subscribers", "_subscribers_to_all"]

    def __init__(self) -> None:
        """Initialize observable properties."""
        self._subscribers: DefaultDict = defaultdict(list)
        self._subscribers_to_all: List[Callable] = []

    def subscribe(self, topic: Any, callback: Callable) -> None:
        """
        Subscribe to a topic.

        The callback for this subscription is called any time the topic
        is published to. The arguments passed to the callable depend on the
        payload given by notifier.

        Parameters
        ----------
        topic
            The topic to subscribe to. Any time this class notifies this topic,
            the callback function is called.

        callback
            The callback function to call when the given topic is notified
            of an event.
        """
        self._subscribers[topic].append(callback)

    def subscribe_all(self, callback: Callable) -> None:
        """
        Subscribe to all topics.

        The callback for this subscription is called any time any topic
        is published to. The arguments passed to the callable depend on the
        payload given by notifier.

        Parameters
        ----------
        callback
            The callback function to call when any topic is notified
            of an event.
        """
        self._subscribers_to_all.append(callback)

    def notify_topic(self, topic: Any, **payload: Any) -> None:
        """
        Notify a topic of an event.

        This calls any callbacks that have been registered to listen
        for notifications to this topic. The payload can be any assortment
        of key-value pairs.

        Parameters
        ----------
        topic
            The topic to notify.

        **payload
            Any assortment of key-value pairs to give to the callback functions.
        """
        for callback in self._subscribers[topic]:
            callback(**payload)

        for callback in self._subscribers_to_all:
            callback(**payload)
