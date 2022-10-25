import novelpy

ref_cooc = novelpy.utils.cooc_utils.create_cooc(
                client_name="mongodb://localhost:27017",
                db_name = "openAlex_novelty",
                collection_name = "concepts",
                year_var="publication_year",
                var = "concepts",
                sub_var = "display_name",
                time_window = range(1984,2022),
                weighted_network = True, self_loop = True)

ref_cooc.main()