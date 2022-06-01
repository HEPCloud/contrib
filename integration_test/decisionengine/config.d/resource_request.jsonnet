local de_std = import 'de_std.libsonnet';
local channels = [
  import 'job_classification.libsonnet',
];

{
  sources: de_std.sources_from(channels) {
    factoryglobal_manifests: {
      module: "decisionengine_modules.glideinwms.sources.factory_global",
      parameters: {
        condor_config: "/etc/condor/condor_config",
        factories: [
          {
            collector_host: "fermicloud576.fnal.gov",
            classad_attrs: []
          },
        ],
        schedule: 300
      }
    },
  "FactoryEntriesSource": {
      module: "decisionengine_modules.glideinwms.sources.factory_entries",
      parameters: {
        condor_config: "/etc/condor/condor_config",
        factories: [
          {
            collector_host: "fermicloud576.fnal.gov",
            classad_attrs: [],
            correction_map: {
               "GLIDEIN_Resource_Slots":'',
               "GLIDEIN_CMSSite":'',
               "GLIDEIN_CPUS":1
            }
          },
        ],
        max_retries: 100,
        retry_interval: 20
      },
      schedule: 120
    },
  },
  transforms: de_std.transforms_from(channels) {
    GridFigureOfMerit: {
      module: "decisionengine_modules.glideinwms.transforms.grid_figure_of_merit",
      parameters: {
        price_performance: 0.9
      }
    },
    glideinwms_requests: {
      module: "decisionengine_modules.glideinwms.transforms.glidein_requests",
      parameters: {
        accounting_group: "de_test",
        fe_config_group: "opportunistic",
        job_filter: "ClusterId > 0"
      }
    }
  },
  logicengines: {
    logicengine1: {
      module: "decisionengine.framework.logicengine.LogicEngine",
      parameters: {
        rules: {
          publish_glidein_requests: {
            expression: "(publish_requests)",
            actions: [
              "glideclientglobal_manifests",
              "glideclient_manifests"
            ],
            facts: []
          },
          publish_grid_requests: {
            expression: "(allow_grid)",
            actions: [],
            facts: [
              "allow_grid_requests"
            ]
          }
        },
        facts: {
          publish_requests: "(True)",
          allow_grid: "(True)",
          allow_lcf: "(True)",
          allow_gce: "(True)",
          allow_aws: "(True)"
        }
      }
    }
  },
  publishers: de_std.publishers_from(channels) {
    glideclientglobal_manifests: {
      module: "decisionengine_modules.glideinwms.publishers.glideclientglobal",
      parameters: {
        condor_config: "/etc/condor/condor_config",
        x509_user_proxy: "/var/de/fe_proxy",
        max_retries: 1,
        retry_interval: 2
      }
    },
    glideclient_manifests: {
      module: "decisionengine_modules.glideinwms.publishers.fe_group_classads",
      parameters: {
        condor_config: "/etc/condor/condor_config",
        x509_user_proxy: "/var/de/fe_proxy",
        max_retries: 1,
        retry_interval: 2
      }
    }
  }
}
