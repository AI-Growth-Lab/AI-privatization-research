import novelpy

ref_cooc = novelpy.utils.cooc_utils.create_cooc(
                client_name="mongodb://localhost:27017",
                db_name = "openAlex_novelty",
                collection_name = "references",
                year_var="publication_year",
                var = "referenced_works",
                sub_var = "journal",
                weighted_network = True, self_loop = True)

ref_cooc.main()