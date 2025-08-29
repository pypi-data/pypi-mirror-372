"""This submodule holds the base classes for Processors,
that form the main building blocks auf an audio processing chain.
These classes hold the underlying ACore object and hanled their initialization, connection,
and `threading.Event()` or `queueing.Queue()` based communication
with the main program during an active audio stream."""
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple

from .io import Input, Output

if TYPE_CHECKING:
    from .acore import AAnalyzer, AEffect, AGenerator
    from .interface import Interface
    from .typing import ACore, InAs

logger = logging.getLogger(__name__)


class Processor(ABC):
    def __init__(self, interface: "Interface") -> None:
        self._interface = interface

    @property
    @abstractmethod
    def acore(self) -> "ACore":
        """Returns the ACore element of the processor."""

    @abstractmethod
    def update_acore(self) -> None:
        """Set in_as and out_chs of acore. This is called by the inputs/outputs."""


class Generator(Processor):
    def __init__(self, agenerator: "AGenerator",
                 interface: "Interface",
                 outputs: Tuple["Output", ...],
                 out_update: bool) -> None:
        """This is the base class for generators, holding the audio generator.

        Args:
            agenerator: Reference to the corresponding ACore object.
            interface: Reference to an Interface instance.
            outputs: A tuple of Output instances.
            out_update: Flag that decides if dynamic output updates are enabled.
        """
        self._agenerator = agenerator
        self._outputs = outputs
        self._out_update = out_update
        # update_acore() is not called here, because it is called on the first connection anyways!
        super().__init__(interface)

    @property
    def acore(self) -> "AGenerator":
        return self._agenerator

    @property
    def outputs(self) -> Tuple["Output", ...]:
        return self._outputs

    def output(self, idx: int = 0) -> "Output":
        """Get the Output for the given index.
        For multiple output Generators that support output-update.
        when the index is +1 of the existing Output(s) a new Output is added.

        Args:
            idx: Index in zero indexed list of Outputs.

        Returns:
            Reference to Output object.
        """
        while idx > len(self._outputs) - 1 and self._out_update:
            self._outputs += (Output(self), )
        return self._outputs[idx]

    def update_acore(self) -> None:
        self._agenerator.out_chs = len(self._outputs)


class Effect(Processor):
    def __init__(self, aeffect: "AEffect",
                 interface: "Interface",
                 inputs: Tuple["Input", ...],
                 outputs: Tuple["Output", ...],
                 in_update: bool,
                 out_update: bool) -> None:
        """This is the base class for effects, holding the audio effect.

        Args:
            aeffect: Reference to the corresponding ACore object.
            interface: Reference to an Interface instance.
            inputs: A tuple of Input instances.
            outputs: A tuple of Output instances.
            in_update: Flag that decides if dynamic input updates are enabled.
            out_update: Flag that decides if dynamic output updates are enabled.

        Notes:
            If both update flags are enabled, input and output counts are syncronized.
        """
        self._aeffect = aeffect
        self._inputs = inputs
        self._outputs = outputs
        self._in_update = in_update
        self._out_update = out_update
        # update_acore() is not called here, because it is called on the first connection anyways!
        super().__init__(interface)

    @property
    def acore(self) -> "AEffect":
        return self._aeffect

    @property
    def outputs(self) -> Tuple["Output", ...]:
        return self._outputs

    def input(self, idx: int = 0) -> "Input":
        """Get the Input for the given index.
        For multiple input Effects that support input-update.
        when the index is +1 of the existing Input(s) a new Input is added.
        When output-update is also supported, Input(s) and Output(s) are syncronized.

        Args:
            idx: Index in zero indexed list of Inputs.

        Returns:
            Reference to Input object.
        """
        while idx > len(self._inputs) - 1 and self._in_update:
            self._inputs += (Input(self), )
            # if update flags are true, keep channel count equal
            if self._out_update:
                self._outputs += (Output(self), )
        return self._inputs[idx]

    def output(self, idx: int = 0) -> "Output":
        """Get the Output for the given index.
        For multiple output Effects that support output-update.
        when the index is +1 of the existing Output(s) a new Output is added.
        When input-update is also supported, Input(s) and Output(s) are syncronized.

        Args:
            idx: Index in zero indexed list of Outputs.

        Returns:
            Reference to Output object.
        """
        while idx > len(self._outputs) - 1 and self._out_update:
            self._outputs += (Output(self), )
            # if update flags are true, keep channel count equal
            if self._in_update:
                self._inputs += (Input(self), )
        return self._outputs[idx]

    def update_acore(self) -> None:
        # create in_as tuple
        in_as: "InAs" = ()
        for inp in self._inputs:
            # add proper connection constraint
            if inp.connected_output is None:
                in_as = in_as + ((None, 0), )
                logger.info(f"Input {inp} is not yet connected to any outputs.")
            else:
                # find channel idx it is connected to
                in_as = in_as + ((inp.connected_output.acore, inp.connected_output.idx), )
        self._aeffect.in_as = in_as
        # count outputs that have a connection
        self._aeffect.out_chs = len(self._outputs)


class Analyzer(Processor):
    def __init__(self, aanalyzer: "AAnalyzer",
                 interface: "Interface",
                 inputs: Tuple["Input", ...],
                 in_update: bool) -> None:
        """This is the base class for analyzers, holding the audio analyzer.

        Args:
            aanalyzer: Reference to the corresponding ACore object.
            interface: Reference to an Interface instance.
            inputs: A tuple of Input instances.
            in_update: Flag that decides if dynamic input updates are enabled.
        """
        self._aanalyzer = aanalyzer
        self._inputs = inputs
        self._in_update = in_update
        # add to analyzer list in interface
        interface.analyzers = interface.analyzers + (self, )
        # update_acore() is not called here, because it is called on the first connection anyways!
        super().__init__(interface)

    @property
    def acore(self) -> "AAnalyzer":
        return self._aanalyzer

    @property
    def inputs(self) -> Tuple[Input, ...]:
        return self._inputs

    @inputs.setter
    def inputs(self, value: Tuple[Input, ...]) -> None:
        self._inputs = value
        self.update_acore()

    @property
    def in_update(self) -> bool:
        return self._in_update

    @in_update.setter
    def in_update(self, value: bool) -> None:
        self._in_update = value

    def input(self, idx: int = 0) -> "Input":
        """Get the Input for the given index.
        For multiple input Effects that support input-update.
        when the index is +1 of the existing Input(s) a new Input is added.

        Args:
            idx: Index in zero indexed list of Inputs.

        Returns:
            Reference to Input object.
        """
        while idx > len(self._inputs) - 1 and self._in_update:
            self._inputs += (Input(self), )
        return self._inputs[idx]

    def update_acore(self) -> None:
        # create in_as tuple
        in_as: "InAs" = ()
        for inp in self._inputs:
            # add proper connection constraint
            if inp.connected_output is None:
                in_as = in_as + ((None, 0), )
                logger.info(f"Input {inp} is not yet connected to any outputs.")
            else:
                # find channel idx it is connected to
                in_as = in_as + ((inp.connected_output.acore, inp.connected_output.idx), )
        self._aanalyzer.in_as = in_as
