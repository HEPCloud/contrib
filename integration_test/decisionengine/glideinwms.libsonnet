{
    "advertise_delay": "5",
    "advertise_with_multiple": "True",
    "advertise_with_tcp": "True",
    "downtimes_file": "frontenddowntime",
    "frontend_monitor_index_page": "False",
    "frontend_name": "@FERMICLOUDNODE@",
    "frontend_versioning": "False",
    "group_parallel_workers": "2",
    "loop_delay": "60",
    "restart_attempts": "3",
    "restart_interval": "1800",

    "config": {
        "ignore_down_entries": "False",
        "idle_vms_total": {
            "curb": "200",
            "max": "1000"
        },
        "idle_vms_total_global": {
            "curb": "200",
            "max": "1000"
        },
        "running_glideins_total": {
            "curb": "90000",
            "max": "100000"
        },
        "running_glideins_total_global": {
            "curb": "90000",
            "max": "100000"
        }
    },

    "high_availability": {
        "check_interval": "300",
        "enabled": "False",
        "ha_frontends": {}
    },

    "log_retention": {
        "process_logs": [
            {
                "backup_count": "5",
                "compression": "",
                "extension": "info",
                "max_days": "7.0",
                "max_mbytes": "100.0",
                "min_days": "3.0",
                "msg_types": "INFO"
            },
            {
                "backup_count": "5",
                "compression": "",
                "extension": "err",
                "max_days": "7.0",
                "max_mbytes": "100.0",
                "min_days": "3.0",
                "msg_types": "DEBUG,ERR,WARN,EXCEPTION"
            }
        ]
    },

    "match": {
        "match_expr": "True",
        "start_expr": "True",
        "factory": {
            "query_expr": "True",
            "match_attrs": {},
            "collectors": [
                {
                    "DN": "/DC=org/DC=incommon/C=US/ST=Illinois/O=Fermi Research Alliance/OU=Fermilab/CN=fermicloud576.fnal.gov",
                    "comment": "Test Factory",
                    "factory_identity": "gfactory@fermicloud576.fnal.gov",
                    "my_identity": "decisionengine_service@fermicloud576.fnal.gov",
                    "node": "fermicloud576.fnal.gov"
                }
            ]
        },
        "job": {
            "comment": "Define job constraint and schedds globally for simplicity",
            "query_expr": "(JobUniverse==5)&&(GLIDEIN_Is_Monitor =!= TRUE)&&(JOB_Is_Monitor =!= TRUE)",
            "match_attrs": {},
            "schedds": [
                {
                    "DN": "/DC=org/DC=incommon/C=US/ST=Illinois/O=Fermi Research Alliance/OU=Fermilab/CN=@FERMICLOUDNODE@.fnal.gov",
                    "fullname": "@FERMICLOUDNODE@.fnal.gov"
                }
            ]
        }
    },

    "monitor": {
        "base_dir": "/var/lib/gwms-frontend/web-area/monitor",
        "flot_dir": "/usr/share/javascriptrrd/flot",
        "javascriptRRD_dir": "/usr/share/javascriptrrd/js",
        "jquery_dir": "/usr/share/javascriptrrd/flot"
    },

    "monitor_footer": {
        "display_txt": "",
        "href_link": ""
    },

    "security": {
        "classad_proxy": "/var/de/fe_proxy",
        "comment": "Test DE at @FERMICLOUDNODE@.fnal.gov",
        "proxy_DN": "/DC=org/DC=incommon/C=US/ST=Illinois/O=Fermi Research Alliance/OU=Fermilab/CN=@FERMICLOUDNODE@.fnal.gov",
        "proxy_selection_plugin": "ProxyAll",
        "security_name": "decisionengine_service",
        "sym_key": "aes_256_cbc",
        "credentials": [
            {
                "absfname": "/var/de/vo_proxy",
                "security_class": "frontend",
                "trust_domain": "grid",
                "type": "grid_proxy"
            }
        ]
    },

    "stage": {
        "base_dir": "/var/lib/gwms-frontend/web-area/stage",
        "use_symlink": "True",
        "web_base_url": "http://@FERMICLOUDNODE@.fnal.gov/vofrontend/stage"
    },

    "work": {
        "base_dir": "/var/lib/gwms-frontend/vofrontend",
        "base_log_dir": "/var/log/gwms-frontend"
    },

    "attrs": {
        "ALL_DEBUG": {
            "glidein_publish": "True",
            "job_publish": "True",
            "parameter": "True",
            "type": "expr",
            "value": "D_SECURITY,D_FULLDEBUG"
        },
        "GLIDECLIENT_Rank": {
            "glidein_publish": "False",
            "job_publish": "False",
            "parameter": "True",
            "type": "string",
            "value": "1"
        },
        "GLIDEIN_Expose_Grid_Env": {
            "glidein_publish": "True",
            "job_publish": "True",
            "parameter": "False",
            "type": "string",
            "value": "True"
        },
        "USE_MATCH_AUTH": {
            "glidein_publish": "False",
            "job_publish": "False",
            "parameter": "True",
            "type": "string",
            "value": "True"
        }
    },

    "groups": {
        "de_test": {
            "enabled": "True",
            "config": {
                "ignore_down_entries": "",
                "glideins_removal": {
                    "margin": "0",
                    "requests_tracking": "False",
                    "type": "NO",
                    "wait": "0"
                },
                "idle_glideins_lifetime": {
                    "max": "0"
                },
                "idle_glideins_per_entry": {
                    "max": "100",
                    "reserve": "5"
                },
                "idle_vms_per_entry": {
                    "curb": "5",
                    "max": "100"
                },
                "idle_vms_total": {
                    "curb": "200",
                    "max": "1000"
                },
                "processing_workers": {
                    "matchmakers": "3"
                },
                "running_glideins_per_entry": {
                    "max": "10000",
                    "min": "0",
                    "relative_to_queue": "1.15"
                },
                "running_glideins_total": {
                    "curb": "90000",
                    "max": "100000"
                }
            },
            "match": {
                "match_expr": "True",
                "start_expr": "True",
                "factory": {
                    "query_expr": "True",
                    "match_attrs": {},
                    "collectors": {}
                },
                "job": {
                    "query_expr": "True",
                    "match_attrs": {},
                    "schedds": {}
                }
            },
            "security": {
                "credentials": {}
            },
            "attrs": {},
            "files": {}
        }
    },

    "ccbs": {},

    "collectors": [
        {
            "DN": "/DC=org/DC=incommon/C=US/ST=Illinois/O=Fermi Research Alliance/OU=Fermilab/CN=@FERMICLOUDNODE@.fnal.gov",
            "group": "default",
            "node": "@FERMICLOUDNODE@.fnal.gov:9618",
            "secondary": "False"
        },
        {
            "DN": "/DC=org/DC=incommon/C=US/ST=Illinois/O=Fermi Research Alliance/OU=Fermilab/CN=@FERMICLOUDNODE@.fnal.gov",
            "group": "default",
            "node": "@FERMICLOUDNODE@.fnal.gov:9618?sock=collector1-40",
            "secondary": "True"
        }
    ],

    "files": {}
}
