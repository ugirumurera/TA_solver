# obj_list = self.otm_api.get_output_data()
#
# with closing(Pool(processes=2)) as p:
#     all_costs = (p.map(set_costs, obj_list))
#     p.terminate()