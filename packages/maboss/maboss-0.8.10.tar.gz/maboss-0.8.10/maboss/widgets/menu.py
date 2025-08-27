
menu = [
    {'name': 'Load MaBoSS file',
     'snippet': ["masim = maboss.load(\"filename.bnd\", \"filename.cfg\")"]},

    {'name': 'Network',
     'sub-menu': [
         {'name': 'Set initial state probability',
          'snippet': ["masim.network.set_istate('nodeA', [prob_OFF, prob_ON])"]},
         {'name': 'Get initial state',
          'snippet': ["masim.get_initial_state()"]}
     ]},

    {'name': 'Simulation',
     'sub-menu': [
          {'name': 'Apply mutant',
           'snippet': ["masim.mutate('nodeA', 'ON') #or 'OFF'"]},

          {'name': 'Run',
           'snippet': ["simres = masim.run()"]},

          {'name': 'Set initial states',
           'snippet': ["masim.network.set_istate([\"mygenelist\"],{})"]},

          {'name': 'Set output',
           'snippet': ["masim.network.set_output(('nodeA', 'nodeB',))"]},

     ]},

    {'name': 'Results',
     'sub-menu': [
                  {'name': 'Save results',
                   'snippet': ["simres.save(\"filename\")"]},

                  {'name': 'Plot piechart',
                   'snippet': ["simres.plot_piechart()"]},

                  {'name': 'Plot trajectory',
                   'snippet': ["simres.plot_trajectory()"]}]
     },
     {'name': 'Conversion',
     'sub-menu': [
                  {'name': 'Convert to biolqm',
                   'snippet': ["biolqm_model = maboss.to_biolqm(masim)"]},

                  {'name': 'Convert to minibn',
                   'snippet': ["minibn_model = maboss.to_minibn(masim)"]},
     ]},
     "---",
     {"name": "Documentation",
        "external-link": "http://pymaboss.readthedocs.io"}
]

toolbar = None
js_api = {}
