INCLUDE_DIRECTORIES(.)
LINK_DIRECTORIES(${BUILD_DIR}/src)

find_package(Protobuf REQUIRED)

SET(NetworkInterface_SRCS
     NetworkInterface.hpp
     NetworkInterface.cpp
     NetworkInterfaceUDPThread.hpp
     NetworkInterfaceUDPThread.cpp
     StelleriumNetworkInterfacePacket.pb.h
     StelleriumNetworkInterfacePacket.pb.cc
)

SET(NetworkInterface_RES ../NetworkInterface.qrc)
QT5_ADD_RESOURCES(NetworkInterface_RES_CXX ${NetworkInterface_RES})
SET(extLinkerOption ${JPEG_LIBRARIES} ${PNG_LIBRARIES} ${OPENGL_LIBRARIES})

ADD_LIBRARY(NetworkInterface-static STATIC ${NetworkInterface_SRCS} ${NetworkInterface_RES_CXX})
QT5_USE_MODULES(NetworkInterface-static Core Network Widgets)
# The library target "NetworkInterface-static" has a default OUTPUT_NAME of "NetworkInterface-static", so change it.
SET_TARGET_PROPERTIES(NetworkInterface-static PROPERTIES OUTPUT_NAME "NetworkInterface")
TARGET_LINK_LIBRARIES(NetworkInterface-static ${extLinkerOption} ${PROTOBUF_LIBRARY})
SET_TARGET_PROPERTIES(NetworkInterface-static PROPERTIES COMPILE_FLAGS "-DQT_STATICPLUGIN")
ADD_DEPENDENCIES(AllStaticPlugins NetworkInterface-static)
