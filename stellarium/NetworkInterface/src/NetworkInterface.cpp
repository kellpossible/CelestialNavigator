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


#include "VecMath.hpp"
#include "StelProjector.hpp"
#include "StelPainter.hpp"
#include "StelApp.hpp"
#include "StelCore.hpp"
#include "StelLocaleMgr.hpp"
#include "StelModuleMgr.hpp"
#include "StelUtils.hpp"
#include "StelFileMgr.hpp"
#include "LandscapeMgr.hpp"
#include "NetworkInterface.hpp"
#include "StelGui.hpp"
#include "StelGuiItems.hpp"
#include "NetworkInterfaceUDPThread.hpp"
#include "StelLocation.hpp"
#include "StelObserver.hpp"
#include "StelleriumNetworkInterfacePacket.pb.h"

#include <QDebug>
#include <QPixmap>
#include <QSettings>
#include <QKeyEvent>
#include <QtNetwork>
#include <cmath>
#include <QSettings>
#include <QDateTime>

StelModule* NetworkInterfaceStelPluginInterface::getStelModule() const
{
	return new NetworkInterface();
}

StelPluginInfo NetworkInterfaceStelPluginInterface::getPluginInfo() const
{
	// Allow to load the resources when used as a static plugin
	Q_INIT_RESOURCE(NetworkInterface);

	StelPluginInfo info;
	info.id = "NetworkInterface";
	info.displayedName = N_("Network Interface");
    info.authors = "Luke Frisken";
    info.contact = "l.frisken@gmail.com";
    info.description = N_("Provides a basic UDP network interface to stellarium");
	info.version = NETWORKINTERFACE_VERSION;
	return info;
}

NetworkInterface::NetworkInterface()
	: displayedAtStartup(false)
	, markColor(1,1,1)
	, toolbarButton(NULL)
	, cardinalPointsState(false)
{
	setObjectName("NetworkInterface");
	conf = StelApp::getInstance().getSettings();
}

NetworkInterface::~NetworkInterface()
{
	//
}

//! Determine which "layer" the plugin's drawing will happen on.
double NetworkInterface::getCallOrder(StelModuleActionName actionName) const
{
	if (actionName==StelModule::ActionDraw)
		return StelApp::getInstance().getModuleMgr().getModule("LandscapeMgr")->getCallOrder(actionName)+10.;
	return 0;
}

void NetworkInterface::init()
{
    GOOGLE_PROTOBUF_VERIFY_VERSION;
    udpThread = new NetworkInterfaceUDPThread();
    udpThread->start();
	// Because the plug-in has no configuration GUI, users rely on what's
	// written in the configuration file to know what can be configured.
	Q_ASSERT(conf);
	if (!conf->childGroups().contains("NetworkInterface"))
		restoreDefaultConfiguration();

	loadConfiguration();

	try
	{
		addAction("actionShow_Network_Interface", N_("Network Interface"), N_("Network Interface"), "marksVisible");

		StelGui* gui = dynamic_cast<StelGui*>(StelApp::getInstance().getGui());
		if (gui != NULL)
		{
			toolbarButton = new StelButton(NULL,
						       QPixmap(":/networkInterface/bt_compass_on.png"),
						       QPixmap(":/networkInterface/bt_compass_off.png"),
						       QPixmap(":/graphicGui/glow32x32.png"),
						       "actionShow_Network_Interface");
			gui->getButtonBar()->addButton(toolbarButton, "065-pluginsGroup");			
		}
		connect(GETSTELMODULE(LandscapeMgr), SIGNAL(cardinalsPointsDisplayedChanged(bool)), this, SLOT(cardinalPointsChanged(bool)));
		cardinalPointsState = false;

		setNetworkInterface(displayedAtStartup);
	}
	catch (std::runtime_error& e)
	{
		qWarning() << "WARNING: unable create toolbar button for NetworkInterface plugin: " << e.what();
	}


}

//! Draw any parts on the screen which are for our module
void NetworkInterface::draw(StelCore* core)
{
    udpThread->packetsQueueMutex.lock();
    while(!udpThread->packetsQueue.isEmpty())
    {
        NetworkInterfacePacket packet = udpThread->packetsQueue.dequeue();
        QString debugString = QString(packet.DebugString().c_str());
        qWarning() << "decoded message: " << debugString;

        if (packet.has_location())
        {
            double latitude = packet.location().latitude();
            QString absLatitudeString = QString::number(abs(latitude));
            double longitude = packet.location().longitude();
            QString absLongitudeString =  QString::number(abs(longitude));
            double altitude = packet.location().altitude();

            QString latitudeString;

            if (latitude >= 0)
            {
                latitudeString = QString("%1%2").arg(absLatitudeString, QString("N"));
            } else {
                latitudeString = QString("%1%2").arg(absLatitudeString, QString("S"));
            }

            QString longitudeString;

            if (longitude >= 0)
            {
                longitudeString = QString("%1%2").arg(absLongitudeString, QString("E"));
            } else {
                longitudeString = QString("%1%2").arg(absLongitudeString, QString("W"));
            }

            QString vehicleName = QString(packet.vehiclename().c_str());

            QString altitudeString = QString::number(altitude);

            QString locationLine = QString("%1\t\t\tX\t0\t%2\t%3\t%4\t2\t\tEarth\t").arg(vehicleName, latitudeString, longitudeString, altitudeString);

            qWarning() << "location line: " << locationLine;

            StelLocation location = StelLocation::createFromLine(locationLine);
            core->moveObserverTo(location);
        }

        if (packet.has_time())
        {
            QSettings * settings = StelApp::getInstance().getSettings();
            Q_ASSERT(settings);
            qDebug() << "time zone: " << settings->value("localization/time_zone");

            QString timeString = QString(packet.time().c_str());
            QDateTime dateTime = QDateTime::fromString(timeString, Qt::ISODate);

            qDebug() << "incoming time :" << timeString;
            qDebug() << "time :" << dateTime.toString();
            qDebug() << "timespec :" << dateTime.timeSpec();

            double jd;
            StelUtils::getJDFromDate(&jd,
                                     dateTime.date().year(),
                                     dateTime.date().month(),
                                     dateTime.date().day(),
                                     dateTime.time().hour(),
                                     dateTime.time().minute(),
                                     dateTime.time().second());
            StelApp::getInstance().getCore()->setJD(jd);
        }
    }
    udpThread->packetsQueueMutex.unlock();
//    currentLocation += 0.1;
//    if (currentLocation > 90)
//    {
//        currentLocation = currentLocation - 180;
//    }
//    qWarning() << "Current Location: " << core->getCurrentLocation().serializeToLine();
//    StelLocation location = StelLocation::createFromLine(QString("Aircraft\t737\tBoeing\tX\t0\t%1S\t145.153305E\t100000\t2\t\tEarth\t").arg(currentLocation));
//    core->moveObserverTo(location);

}

void NetworkInterface::update(double deltaTime)
{
	markFader.update((int)(deltaTime*1000));
}

void NetworkInterface::setNetworkInterface(bool b)
{
	if (b == markFader)
		return;
	if (b)
	{
		// Save the display state of the cardinal points and hide them.
		cardinalPointsState = GETSTELMODULE(LandscapeMgr)->getFlagCardinalsPoints();
		GETSTELMODULE(LandscapeMgr)->setFlagCardinalsPoints(false);
	} else {
		// Restore the cardinal points state.
		GETSTELMODULE(LandscapeMgr)->setFlagCardinalsPoints(cardinalPointsState);
	}
	markFader = b;
	// autosaving the state by default
	displayedAtStartup = b;
	conf->setValue("NetworkInterface/enable_at_startup", displayedAtStartup);
	emit networkInterfaceChanged(b);
}

void NetworkInterface::loadConfiguration()
{
	Q_ASSERT(conf);
	conf->beginGroup("NetworkInterface");
	markColor = StelUtils::strToVec3f(conf->value("mark_color", "1,0,0").toString());
	font.setPixelSize(conf->value("font_size", 10).toInt());
	displayedAtStartup = conf->value("enable_at_startup", false).toBool();
	conf->endGroup();
}

void NetworkInterface::restoreDefaultConfiguration()
{
	Q_ASSERT(conf);
	// Remove the whole section from the configuration file
	conf->remove("NetworkInterface");
	// Load the default values...
	loadConfiguration();	
	// But this doesn't save the color, so...
	conf->beginGroup("NetworkInterface");
	conf->setValue("mark_color", "1,0,0");
	conf->endGroup();
}

void NetworkInterface::cardinalPointsChanged(bool b)
{
	if (b && getNetworkInterface()) {
		cardinalPointsState = true;
		setNetworkInterface(false);
	}
}
