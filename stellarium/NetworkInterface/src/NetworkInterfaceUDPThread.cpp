/*
 * Copyright (C) 2016 Luke Frisken
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Suite 500, Boston, MA  02110-1335, USA.
 */

#include <QDebug>
#include <QObject>
#include <QHostAddress>
#include <QByteArray>
#include <QtGlobal>
#include <QString>
#include <QMutex>
#include <QMutexLocker>

#include "NetworkInterfaceUDPThread.hpp"
#include "StelleriumNetworkInterfacePacket.pb.h"


NetworkInterfaceUDPThread::NetworkInterfaceUDPThread(QObject *parent)
{
    abort = false;
}

void NetworkInterfaceUDPThread::decodeMessage(QByteArray datagram) {
    QString s_data = QString::fromLatin1(datagram);
    NetworkInterfacePacket packet;
    packet.ParseFromArray(datagram, datagram.size());

    packetsQueueMutex.lock();
    packetsQueue.enqueue(packet);
    packetsQueueMutex.unlock();
}

void NetworkInterfaceUDPThread::run()
{
    udpSocket = new QUdpSocket(this);
    udpSocket->bind(QHostAddress::LocalHost, 7755);
    forever {
        this->sleep(1);
        qWarning() << "thread is running, reading pending datagrams";

        while (udpSocket->hasPendingDatagrams())
        {
            QByteArray datagram;
            datagram.resize(udpSocket->pendingDatagramSize());
            QHostAddress sender;
            quint16 senderPort;

            udpSocket->readDatagram(datagram.data(), datagram.size(),
                                    &sender, &senderPort);

            qWarning() << "Sender From: " << sender.toString();

            decodeMessage(datagram);
        }
    }
}

NetworkInterfaceUDPThread::~NetworkInterfaceUDPThread()
{
    abort = true;
}
