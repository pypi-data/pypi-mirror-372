from dataclasses import dataclass

from kywy.client.kawa_decorators import KawaScriptInput, KawaScriptOutput, KawaScriptParameter


@dataclass
class Metadata:
    inputs: list[KawaScriptInput]
    parameters: list[KawaScriptParameter]
    outputs: list[KawaScriptOutput]

    name_for_anonymous_dataframe = 'df'

    def dataframesOrDefaultName(self) -> list[str]:
        dataframes = []
        if len(self.inputs) == 1 and self.inputs[0].dataframe is None:
            return []
        for input_item in self.inputs:
            dataframeName = input_item.dataframe or Metadata.name_for_anonymous_dataframe
            if dataframeName not in dataframes:
                dataframes.append(dataframeName)
        return dataframes

    def has_outputs(self) -> bool:
        return len(self.outputs) > 0

    @classmethod
    def from_deserialized_json(cls, deserialized_json):
        _inputs = deserialized_json.get('parameters') or []
        _params = deserialized_json.get('scriptParameters') or []
        _outputs = deserialized_json.get('outputs') or []

        inputs = [KawaScriptInput(dataframe=json_item.get('dataframe'), name=json_item['name'], type=json_item['type'])
                  for json_item in _inputs]
        # TODO THIERRY ########## workflow: 'default' or 'defaultValue' (or both) ?
        parameters = [KawaScriptParameter(json_item['name'],
                                          json_item['type'],
                                          json_item.get('defaultValue', None),
                                          json_item.get('description', ''),
                                          json_item.get('values', []),
                                          json_item.get('extensions', []))
                      for json_item in _params]
        outputs = [KawaScriptOutput(name=json_item['name'], type=json_item['type'])
                   for json_item in _outputs]

        return Metadata(inputs, parameters, outputs)
