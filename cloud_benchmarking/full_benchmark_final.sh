echo "Enter IP to benchmark: "
read ip_fin
echo "Enter instance name: (E.g: M4_4xlarge)"
read inst_name
echo "Enter security key: "
read sec_key

#copy dependencies over to machine that is benchmarking
cd
scp -i $sec_key.pem oldbenchmark.tar run_DB12.sh full_benchmark_for_AWS.sh root@$ip_fin:/root
scp -i $sec_key.pem use_lvm_for_cms_wn_nvme root@$ip_fin:/usr/libexec/gco_startup/
# ssh -i $sec_key.pem root@$ip_fin

#run files on other machine
ssh -i $sec_key.pem root@$ip_fin bash full_benchmark_for_AWS.sh

#save results in a corresponding folder on this machine
cd
scp -i $sec_key.pem root@$ip_fin:~/benchmark.txt ./results/$inst_name/benchmark
scp -i $sec_key.pem root@$ip_fin:/root/workdir/suite_results/run_*/bmkrun_report.json ./results/$inst_name/bmkrun_report.json
