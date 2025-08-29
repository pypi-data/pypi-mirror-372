# -*- coding: utf-8 -*-

from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base.base_models import OutputTypes

from sinapsis_huggingface_transformers.helpers.tags import Tags
from sinapsis_huggingface_transformers.templates.base_transformers import TransformersBase

SummarizationTransformersUIProperties = TransformersBase.UIProperties
SummarizationTransformersUIProperties.output_type = OutputTypes.TEXT
SummarizationTransformersUIProperties.tags.extend([Tags.SUMMARIZATION, Tags.TEXT])


class SummarizationTransformers(TransformersBase):
    """Template for text summarization using a Hugging Face Transformers pipeline.

    This class provides a reusable framework for summarizing text using a pre-trained
    Hugging Face model.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: SummarizationTransformers
      class_name: SummarizationTransformers
      template_input: InputTemplate
      attributes:
        model_path: '/path/to/model'
        model_cache_dir: /path/to/cache/dir
        device: 'cuda'
        torch_dtype: float16
        inference_kwargs:
            min_length: 5
            max_length: 20

    """

    SUMMARY_TEXT_KEY = "summary_text"
    UIProperties = SummarizationTransformersUIProperties

    def initialize(self) -> None:
        """Initializes the template's common state for creation or reset.

        This method is called by both `__init__` and `reset_state` to ensure
        a consistent state.
        """
        super().initialize()
        self.task = "summarization"
        self.setup_pipeline()

    def transformation_method(self, container: DataContainer) -> DataContainer:
        """Summarize text using a Transformers Pipeline.

        Args:
            container (DataContainer): DataContainer including the text to be
            summarized.

        Returns:
            DataContainer: DataContainer including the summarized text.
        """
        for text_packet in container.texts:
            summarized_text = self.pipeline(text_packet.content, **self.attributes.inference_kwargs)[0][
                self.SUMMARY_TEXT_KEY
            ]

            text_packet.content = summarized_text
        return container
