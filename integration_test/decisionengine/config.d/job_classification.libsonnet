{
  sources: {
    jobs_manifests: {
      module: "decisionengine_modules.htcondor.sources.job_q",
      parameters: {
        condor_config: "/etc/condor/condor_config",
        collector_host: "@FERMICLOUDNODE@.fnal.gov",
        schedds: [
          "@FERMICLOUDNODE@.fnal.gov"
        ],
        constraint: "True",
        classad_attrs: [
          "ClusterId",
          "ProcId",
          "VO",
          "RequestCpus",
          "RequestMemory",
          "REQUIRED_OS",
          "JobStatus",
          "RequestMaxInputRate",
          "RequestMaxOutputRate",
          "RequestMaxInputDataSize",
          "RequestMaxOutputDataSize",
          "MaxWallTimeMins",
          "x509UserProxyVOName",
          "x509UserProxyFirstFQAN",
          "EnteredCurrentStatus",
          "x509userproxy",
          "JOB_EXPECTED_MAX_LIFETIME",
          "CMS_JobType",
          "DesiredOS",
          "DESIRED_Sites",
          "DESIRED_Resources",
          "DESIRED_usage_model",
          "RequestGPUs"
        ],
        correction_map: {
            RequestMaxInputRate:0,
            RequestMaxOutputRate:0,
            RequestMaxInputDataSize:0,
            RequestMaxOutputDataSize:0,
            DESIRED_usage_model:'',
            DesiredOS:'',
            CMS_JobType:'',
            DESIRED_Sites:'',
            REQUIRED_OS:'',
            VO:'',
            x509UserProxyVOName:'',
            x509userproxy:'',
            x509UserProxyFirstFQAN:'',
            ProcId:0,
            ClusterId:0,
            RequestCpus:0,
            RequestMemory:0,
            MaxWallTimeMins:0,
            JobStatus:0,
            JOB_EXPECTED_MAX_LIFETIME:0,
            EnteredCurrentStatus:0,
            RequestGPUs:0,
            ServerTime:0}
      },
      schedule: 60
    },
    FigureOfMerit: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "AWS_Figure_Of_Merit",
         max_attempts: 100,
         retry_interval: 20
      }
    },
    GceFigureOfMerit: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "GCE_Figure_Of_Merit",
         max_attempts: 100,
         retry_timeout: 20
      }
    },
    NerscFigureOfMerit: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "Nersc_Figure_Of_Merit",
         max_attempts: 100,
         retry_timeout: 20
      }
    },
    Factory_Entries_AWS: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "Factory_Entries_AWS",
         max_attempts: 100,
         retry_timeout: 20
      }
    },
    Factory_Entries_LCF: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "Factory_Entries_LCF",
         max_attempts: 100,
         retry_timeout: 20
      }
    },
    Factory_Entries_Grid: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "Factory_Entries_Grid",
         max_attempts: 100,
         retry_timeout: 20
      }
    },
    Factory_Entries_GCE: {
       module: "decisionengine.framework.modules.EmptySource",
       name: "EmptySource",
       parameters: {
         data_product_name: "Factory_Entries_GCE",
         max_attempts: 100,
         retry_timeout: 20
      }
    },
    StartdManifestsSource: {
      module: "decisionengine_modules.htcondor.sources.slots",
      parameters: {
        classad_attrs: [
          "SlotType",
          "Cpus",
          "TotalCpus",
          "GLIDECLIENT_NAME",
          "GLIDEIN_Entry_Name",
          "GLIDEIN_FACTORY",
          "GLIDEIN_Name",
          "GLIDEIN_Resource_Slots",
          "State",
          "Activity",
          "PartitionableSlot",
          "Memory",
          "GLIDEIN_GridType",
          "TotalSlots",
          "TotalSlotCpus",
          "GLIDEIN_CredentialIdentifier"
        ],
        correction_map : {
          "SlotType":'',
          "Cpus":0,
          "TotalCpus":0,
          "GLIDECLIENT_NAME":'',
          "GLIDEIN_Entry_Name":'',
          "GLIDEIN_FACTORY":'',
          "GLIDEIN_Name":'',
          "GLIDEIN_Resource_Slots":'',
          "State":'',
          "Activity":'',
          "PartitionableSlot":0,
          "Memory":0,
          "GLIDEIN_GridType":'',
          "TotalSlots":0,
          "TotalSlotCpus":0,
          "GLIDEIN_CredentialIdentifier":''
        },
        collector_host: "fermicloud576.fnal.gov",
        condor_config: "/etc/condor/condor_config"
      },
      max_attempts: 100,
      retry_timeout: 20,
      schedule: 320
    },
  },
  transforms: {
    t_job_categorization: {
      module: "decisionengine_modules.glideinwms.transforms.job_clustering",
      parameters: {
        match_expressions: [
          {
            job_bucket_criteria_expr: "(DESIRED_Sites=='ITB_FC_CE2')",
            frontend_group: "de_test",
            site_bucket_criteria_expr: [
              "GLIDEIN_Site=='ITB_FC_CE2'"
            ]
          }
        ],
        job_q_expr: "JobStatus==1"
      }
    }
  },
  publishers: {
    JobClusteringPublisher: {
      module: "decisionengine_modules.glideinwms.publishers.job_clustering_publisher",
      name: "JobClusteringPublisher",
      parameters: {
        publish_to_graphite: true,
        graphite_host: "fifemondata.fnal.gov",
        graphite_port: 2004,
        graphite_context: "hepcloud.de.@FERMICLOUDNODE@.glideinwms",
        output_file: "/etc/decisionengine/modules.data/job_cluster_totals.csv",
        max_retries: 3,
        retry_interval: 2
      }
    }
  }
}
