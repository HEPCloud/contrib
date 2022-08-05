# Remove autoshutdown
service glideinwms-pilot stop
# Extract all files from old benchmark tar
tar -xvf  oldbenchmark.tar

# download git
cd /etc/yum.repos.d/; wget https://cli.github.com/packages/rpm/gh-cli.repo
yum -y install gh
cd

# run use_lvm_for_cms_wn_nvme for machines of 5th gen and above
cd /usr/libexec/gco_startup/
./use_lvm_for_cms_wn_nvme

# move files from container to a place with enough storage
mkdir -p /home/scratchgwms/run/containers
mkdir -p /home/scratchgwms/lib/containers
cd /var/run 
ln -s /home/scratchgwms/run/containers containers
cd /var/lib/ 
ln -s /home/scratchgwms/lib/containers containers
cd

# install podman
yum --disablerepo=epel,osg list podman
yum install -y podman

# run container
podman pull publicregistry.fnal.gov/ssi_images/hepspec-benchmark 

bash run_DB12.sh
bash run_benchmark.sh

for i in {1..180}; do
        foo=`ps -ef | grep start.sh | grep -v grep`
        myrc=$?
        if [ $myrc -ne 0 ]
                then
                echo "Benchmark finished; $myrc"
                bash Calc_HS06.sh
                exit
        else
                echo "Benchmark not finished; $myrc"
                sleep 160
        fi
done
