# import requests
# from ._builder import RCSBQueryBuilder

# __all__ = ["RCSBQueryBuilder"]

# class RCSBQuery:
#     def __init__(self, data):
#         """
#         Recursively converts a dictionary into an object tree.
#         """
#         for key, value in data.items():
#             # If the value is a dictionary, recurse
#             if isinstance(value, dict):
#                 setattr(self, key, RCSBQuery(value))
#             # If the value is a list, check if items are dicts and recurse
#             elif isinstance(value, list):
#                 setattr(self, key, [
#                     RCSBQuery(item) if isinstance(item, dict) else item
#                     for item in value
#                 ])
#             # Otherwise, just set the value (strings, numbers, etc.)
#             else:
#                 setattr(self, key, value)

#     def __str__(self):
#             """
#             Overrides the standard string representation (used by print())
#             to output the content as nicely formatted JSON.
#             """
#             # 1. Convert the object tree back to a Python dictionary
#             data_dict = self.to_dict()
        
#             # 2. Use json.dumps with indent=2 for pretty-printing
#             return json.dumps(data_dict, indent=2)

#     def __repr__(self):
#         # Pretty print the object attributes for debugging
#         return f"RCSBQuery({self.__dict__})"
   

#     def to_dict(self):
#         """Convert back to dictionary if needed"""
#         return json.loads(json.dumps(self, default=lambda o: o.__dict__))

#     # @staticmethod
#     # def get(pdb_id, query):
#     #     response = requests.post("https://data.rcsb.org/graphql", json={"query": query, "variables": {"id": pdb_id}}).json()
#     #     entry_data = response['data']['entry']
#     #     return RCSBQuery(entry_data)

# def query_rcsb(query, entry_id: str):
#     # 1. Generate the query string
#     # query_string = builder.render()
    
#     # 2. Execute the query (Mocking the network call here for demonstration)
#     # In production, you would use:
#     response = requests.post("https://data.rcsb.org/graphql", json={"query": query, "variables": {"id": entry_id}}).json()
#     # data = response.json()['data']['entry']
    
#     # --- START MOCK DATA (Simulating what RCSB would return for your query) ---
#     # mock_api_response = {
#     #     "data": {
#     #         "entry": {
#     #             "polymer_entities": [
#     #                 {
#     #                     "rcsb_id": "4HHB_1",
#     #                     "entity_poly": {"pdbx_seq_one_letter_code_can": "VLSPADKT..."},
#     #                     "uniprots": [{"rcsb_id": "P69905"}]
#     #                 },
#     #                 {
#     #                     "rcsb_id": "4HHB_2",
#     #                     "entity_poly": {"pdbx_seq_one_letter_code_can": "VHLTPEEK..."},
#     #                     "uniprots": [{"rcsb_id": "P68871"}]
#     #                 }
#     #             ],
#     #             "nonpolymer_entities": [
#     #                 {
#     #                     "nonpolymer_comp": {
#     #                         "chem_comp": {"id": "HEM"}
#     #                     },
#     #                     "nonpolymer_entity_instances": [
#     #                         {
#     #                             "rcsb_nonpolymer_instance_validation_score": {
#     #                                 "is_subject_of_investigation": "Yes"
#     #                             }
#     #                         }
#     #                     ]
#     #                 }
#     #             ]
#     #         }
#     #     }
#     # }
#     # --- END MOCK DATA ---

#     entry_data = response['data']['entry']
#     return entry_data
#     # return RCSBQuery(entry_data)

# if __name__ == "__main__":
#     # 1. Build the Query Structure
#     builder = RCSBQueryBuilder()
    
#     (
#         builder
#         .enter("polymer_entities")
#             .add("rcsb_id")
#             .enter("entity_poly").add("pdbx_seq_one_letter_code_can").end()
#             .enter("uniprots").add("rcsb_id").end()
#             .enter("rcsb_target_cofactors").add("cofactor_SMILES", "binding_assay_value").end()
#         .end()
#         .enter("nonpolymer_entities")
#             .enter("nonpolymer_comp")
#                 .enter("chem_comp").add("id").end()
#             .end()
#             .enter("nonpolymer_entity_instances")
#                 .enter("rcsb_nonpolymer_instance_validation_score")
#                     .add("is_subject_of_investigation")
#                 .end()
#             .end()
#         .end()
#     )
#     # 2. Fetch the Object
#     entry = query_rcsb(builder.render(), "4HHB")
#     print(builder.render())


#     print(entry)
#     # 3. Access Data via Dot Notation (Dynamic!)
#     print(f"Type: {type(entry)}") 
#     # Access polymer entities
#     poly_1 = entry.polymer_entities[0]
#     print(f"\nPolymer 1 ID: {poly_1.get("rcsb_id")}")
#     print(f"Sequence: {poly_1.entity_poly.pdbx_seq_one_letter_code_can}")
    
#     # Access non-polymer entities (deeply nested)
#     chem_id = entry.nonpolymer_entities
#     print(f"\nNon-Polymer Chem ID: {chem_id}")
    
#     # Check validation score
#     val_score = entry.nonpolymer_entities[0].nonpolymer_entity_instances[0] \
#                      .rcsb_nonpolymer_instance_validation_score[0].is_subject_of_investigation
#     print(f"Is Subject of Investigation: {val_score}")
