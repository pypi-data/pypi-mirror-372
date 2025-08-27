# -*- coding: utf-8 -*-
from nmdc_api_utilities.data_processing import DataProcessing
from nmdc_api_utilities.data_object_search import DataObjectSearch
from nmdc_api_utilities.workflow_execution_search import WorkflowExecutionSearch

dos_client = DataObjectSearch()

dp_client = DataProcessing()

# Using the DataObjectSearch class to get records from the DataObject collection. We are looking for records with the attribute 'data_object_type' equal to 'FT ICR-MS Analysis Results'.
# We want to get the first 100 records and we want to include the fields 'id', 'md5_checksum', and 'url' in the results. We also want to get all pages of results.
processed_nom = dos_client.get_record_by_attribute(
    attribute_name="data_object_type",
    attribute_value="FT ICR-MS Analysis Results",
    max_page_size=100,
    fields="id,md5_checksum,url",
    all_pages=True,
)
# clarify names
for dataobject in processed_nom:
    dataobject["processed_nom_id"] = dataobject.pop("id")
    dataobject["processed_nom_md5_checksum"] = dataobject.pop("md5_checksum")
    dataobject["processed_nom_url"] = dataobject.pop("url")

# convert to df
processed_nom_df = dp_client.convert_to_df(processed_nom)
print(processed_nom_df.head())
# Next, we query the WorkflowExecution collection. To do so, we need to create an instance of it
we_client = WorkflowExecutionSearch()
# use utility function to get a list of the ids from processed_nom
result_ids = dp_client.extract_field(processed_nom, "processed_nom_id")
# Using the WorkflowExecutionSearch class to get records from the WorkflowExecution collection. We are looking for records with the attribute 'has_output' equal to the list of ids we got from the previous step.
# We use the get_batch_records method to identify records that include any of the ids from the input list, matching the 'has_output' field.
analysis_dataobj = we_client.get_batch_records(
    id_list=result_ids,
    search_field="has_output",
    fields="id,has_input,has_output",
    chunk_size=100,
)

# clarify names
for dataobject in analysis_dataobj:
    dataobject["analysis_id"] = dataobject.pop("id")
    dataobject["analysis_has_input"] = dataobject.pop("has_input")
    dataobject["analysis_has_output"] = dataobject.pop("has_output")

# convert to data frame
analysis_dataobj_df = dp_client.convert_to_df(analysis_dataobj)
