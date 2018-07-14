sudo apt-get install git libboost-dev gcc g++ make cmake libstxxl-dev \
libxml2-dev libbz2-dev zlib1g-dev libzip-dev libboost-filesystem-dev \
libboost-thread-dev libboost-system-dev libboost-regex-dev libboost-program-options-dev \
libboost-iostreams-dev libgomp1 libpng-dev  libprotobuf-dev protobuf-compiler \
liblua5.1-0-dev libluabind-dev pkg-config libosmpbf-dev
git clone https://github.com/DennisOSRM/Project-OSRM.git
mkdir -p build; cd build; cmake ..; make
sudo -E add-apt-repository -y ppa:george-edison55/cmake-3.x
sudo -E apt-get update
sudo apt-get install cmake
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install gcc-5 g++-5
#sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 60 --slave /usr/bin/g++ g++ /usr/bin/g++-5
