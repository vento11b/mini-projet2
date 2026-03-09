CXX =  g++

server: server.cpp
	$(CXX) $< -o $@.exe