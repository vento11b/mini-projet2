#include <iostream>
#include <winsock2.h>

int main() {
    WSADATA wsaData;
    int wsaerr;
    WORD wVersionRequested = MAKEWORD(2, 2);
    wsaerr = WSAStartup(wVersionRequested, &wsaData);


    if (wsaerr != 0) {
        std::cout << "The Winsock dll not found!" << std::endl;
        return 0;
    } else {
        std::cout << "The Winsock dll found" << std::endl;
        std::cout << "The status: " << wsaData.szSystemStatus << std::endl;
    }

    SOCKET serverSocket;
	serverSocket = INVALID_SOCKET;
	serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

	// Check for socket creation success
	if (serverSocket == INVALID_SOCKET) {
	    std::cout << "Error at socket(): " << WSAGetLastError() << std::endl;
	    WSACleanup();
	    return 0;
	} else {
	    std::cout << "Socket is OK!" << std::endl;
	}
    
    return 0;
}