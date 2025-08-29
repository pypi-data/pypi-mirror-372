from .parser import *
from .solver import *

class eqs():
    """
    The eqs class is the only thing that you need to import from this package.
    it gets equations as an attribute and perform parsing and solving.
    """
    def __init__(self, text, do_parse=True, do_solve=True, **kwargs):
        self.text = text
        self.do_solve = do_solve

        settings_kws = ('verbose', 'init_vals', 'max_iter', 'learning_rate', 'random_seed')
        
        for key in kwargs.keys():
            if key not in settings_kws:
                raise ValueError('{} is not a valid keword argument!'.format(key))
            
        self.settings = kwargs
        self.verbose = kwargs.get('verbose', True)

        if do_parse:
            self.parse()

        if do_solve:
            self.vars_vals = self.solve()

    def parse(self):
        """
        This function uses all fynctions from parser module to preform parsing on input equations.
        """
        
        eqs = eqs_extractor(self.text)
 
        eqs_vars = [var_extractor(eq) for eq in eqs]
        
        all_vars = []
        for eq_vars in eqs_vars:
            all_vars.extend(eq_vars)
        all_vars = set(all_vars)

        self.coolprop_map_dict = coolprop_transformer(eqs)

        if self.verbose:
            print('Total number of equations: {}'.format(len(eqs)))
            print('Total number of variables: {}'.format(len(all_vars)))

        if len(eqs) != len(all_vars):
            raise Warning('Total Number of equations and variables does not match!')

        group_labels, total_groups = find_eqs_systems_labels(eqs, eqs_vars)
        if self.verbose:
            print('Number of isolated systems of equations: {}\n'.format(total_groups))
            
        self.eqs_sets, self.var_sets = seperate_eqs_systems(eqs, eqs_vars,
                                                  group_labels, total_groups)

        self.ordered_eqs, self.ordered_vars = ordered_eqs_vars(self.eqs_sets, self.var_sets)

        if self.verbose and  not self.do_solve:
            for system_idx, system in enumerate(self.ordered_eqs):
                print('system number: _{}_'.format(system_idx+1))
                print('number of equations in this system: {}\n'.format(len(self.eqs_sets[system_idx])))
                print('solve\norder       equations')
                print('--------------------------------------------------------------------')
                for sub_system_idx, sub_system in enumerate(system):
                    for eq in sub_system:
                        print('{:4d}       {}'.format(sub_system_idx+1, eq))
                print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_\n')


    def solve(self):
        """
        This function uses all functions inside solver module to perform solving on parsed equations.
        """

        solved_vars = {}
        systems_residuals = []

        for system_eqs, system_vars in zip(self.ordered_eqs, self.ordered_vars):
            results, system_residuals = solve_system(system_eqs, system_vars,
                                                     self.coolprop_map_dict, **self.settings)
            solved_vars.update(results)
            systems_residuals.append(system_residuals)

        self.solved_vars = solved_vars
        self.systems_residuals = systems_residuals

        if self.verbose and self.do_solve:
            for system_idx, system in enumerate(self.ordered_eqs):
                print('system number: _{}_'.format(system_idx+1))
                print('number of equations in this system: {}\n'.format(len(self.eqs_sets[system_idx])))
                print('solve\norder     residual       equations')
                print('--------------------------------------------------------------------')
                for sub_system_idx, sub_system in enumerate(system):
                    for eq, res in zip(sub_system, systems_residuals[system_idx][sub_system_idx]):
                        print('{:4d}       {:.5f}       {}'.format(sub_system_idx+1, res, eq))
                print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_\n')

            print('Values of variables:\n')
            for key, value in solved_vars.items():
                print('{}:    {}'.format(key, value))

        return solved_vars
