import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.0
import QtQuick.Controls 2.15
import "controls"
import "mug"
import QtGraphicalEffects 1.15

Window {
    id: window
    property bool overlayMode: false

    width: (window.overlayMode ? 200 : 300)
    height: (window.overlayMode ? 66 : 400)
    visible: true
    color: "#00000000"
    title: qsTr("Ember Control")

    flags: Qt.Window | Qt.FramelessWindowHint | (window.overlayMode ? Qt.WindowStaysOnTopHint | Qt.WA_TranslucentBackground : 0)

    Mug {
        id: mug
    }

    QtObject {
        id: internal

        function showSettings() {
            var component = Qt.createComponent("Settings.qml")
            var win = component.createObject()
            win.show()
        }

        function toggleOverlayMode() {
            window.overlayMode = !window.overlayMode
        }
    }

    Rectangle {
        id: background
        x: 0
        y: 0
        width: parent.width
        height: parent.height
        color: (window.overlayMode ? "#00000000" : "#ffff5858")
        z: 1
        gradient: Gradient {
            GradientStop {
                id: backgroundGradientStart
                position: 1
                color: "#ff5858"
            }

            GradientStop {
                id: backgroundGradientStop
                position: 0
                color: "#f09819"
            }
        }

        PropertyAnimation {
            id: backgroundAnimationCold2
            target: backgroundGradientStart
            property: "color"
            to: "#0E1533"
            duration: 10000
            running: mug.temperatureType == Mug.TemperatureType.Cold && !window.overlayMode
        }

        PropertyAnimation {
            id: backgroundAnimationCold1
            target: backgroundGradientStop
            property: "color"
            to: "#294663"
            duration: 10000
            running: mug.temperatureType == Mug.TemperatureType.Cold && !window.overlayMode
        }

        PropertyAnimation {
            id: backgroundAnimationWarm2
            target: backgroundGradientStart
            property: "color"
            to: "#873746"
            duration: 10000
            running: mug.temperatureType == Mug.TemperatureType.Warm && !window.overlayMode
        }

        PropertyAnimation {
            id: backgroundAnimationWarm1
            target: backgroundGradientStop
            property: "color"
            to: "#8D6F3E"
            duration: 10000
            running: mug.temperatureType == Mug.TemperatureType.Warm && !window.overlayMode
        }

        PropertyAnimation {
            id: backgroundAnimationHot2
            target: backgroundGradientStart
            property: "color"
            to: "#ff5858"
            duration: 10000
            running: mug.temperatureType == Mug.TemperatureType.Hot && !window.overlayMode
        }

        PropertyAnimation {
            id: backgroundAnimationHot1
            target: backgroundGradientStop
            property: "color"
            to: "#f09819"
            duration: 10000
            running: mug.temperatureType == Mug.TemperatureType.Hot && !window.overlayMode
        }


        Rectangle {
            id: topbar
            height: 32
            color: "#00000000"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            transformOrigin: Item.Center
            anchors.rightMargin: 0
            anchors.leftMargin: 0
            anchors.topMargin: 0

            DragHandler {
                onActiveChanged: if(active){
                                     window.startSystemMove()
                                 }
            }

            Image {
                id: image
                x: 3
                y: 3
                width: 16
                height: 16
                horizontalAlignment: Image.AlignRight
                visible: batteryChargeText.text !== ""
                source: {
                    var batteryImageSource = "SVGs/battery"

                    const chargePostFix = ["-20", "-50", "-50", "-80", ""];

                    const chargeIndex = Math.ceil(Math.max(0, mug.batteryCharge - 30) / 20)

                    batteryImageSource += chargePostFix[chargeIndex];

                    if (mug.charging) {
                        batteryImageSource += "-charging"
                    }

                    return batteryImageSource + ".png"
                }
                cache: true
                autoTransform: false
                sourceSize.height: 40
                sourceSize.width: 40
                fillMode: Image.PreserveAspectFit

            }

            Text {
                id: batteryChargeText
                x: 20
                y: 3
                color: "#ffffff"
                text: (mug.batteryCharge == -1.0 ? "" : String(mug.batteryCharge) + "%")
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                styleColor: "#00000000"
            }

            MenuButton {
                id: close
                visible: !window.overlayMode
                iconSource: "SVGs/close.png"
                x: 265
                anchors.right: parent.right
                anchors.top: parent.top
                btnColorMouseOver: "#dd3c3c"
                anchors.topMargin: 0
                anchors.rightMargin: 0
                onClicked: {
                    backend.close_event()
                    window.close()
                }
            }

            MenuButton {
                id: minimize
                visible: !window.overlayMode
                x: 224
                anchors.right: close.left
                anchors.top: parent.top
                anchors.topMargin: 0
                iconSource: "SVGs/minus.png"
                anchors.rightMargin: 0
                btnColorMouseOver: "#5cffffff"
                onClicked: window.showMinimized()
            }

            MenuButton {
                id: enterOverlay
                visible: !window.overlayMode
                x: 183
                anchors.right: minimize.left
                anchors.top: parent.top
                anchors.topMargin: 0
                iconSource: "SVGs/overlay.png"
                anchors.rightMargin: 0
                btnColorMouseOver: "#5cffffff"
                onClicked: internal.toggleOverlayMode()
            }

            SmallMenuButton {
                id: exitOverlay
                visible: window.overlayMode
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.rightMargin: 0
                iconSource: "SVGs/overlay.png"
                btnColorMouseOver: "#5cffffff"
                onClicked: internal.toggleOverlayMode()
            }
        }

        Rectangle {
            id: content
            color: "#00000000"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: topbar.bottom
            anchors.bottom: parent.bottom
            anchors.rightMargin: 0
            anchors.bottomMargin: (window.overlayMode ? 25 : 55)
            anchors.leftMargin: 0
            anchors.topMargin: 0

            Text {
                id: temperatureText
                x: 89
                y: 138
                color: (window.overlayMode ? "#ff5858" : "#ffffff")
                text: (mug.temperature == -1.0 ? "" : (String(mug.temperature) + "°C"))
                anchors.verticalCenter: parent.verticalCenter
                font.pixelSize: 50
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignTop
                renderType: Text.QtRendering
                anchors.horizontalCenter: parent.horizontalCenter
                style: Text.Normal
                font.styleName: "Regular"
                font.bold: true
            }

            LinearGradient {
                id: temperatureTextGradient
                visible: window.overlayMode
                anchors.fill: temperatureText
                source: temperatureText

                gradient: Gradient {
                    GradientStop {
                        id: temperatureGradientStart
                        position: 1
                        color: "#ff5858"
                    }

                    GradientStop {
                        id: temperatureGradientStop
                        position: 0
                        color: "#f09819"
                    }
                }

                PropertyAnimation {
                    id: temperatureAnimationCold2
                    target: temperatureGradientStart
                    property: "color"
                    to: "#0E1533"
                    duration: 10000
                    running: mug.temperatureType == Mug.TemperatureType.Cold && window.overlayMode
                }

                PropertyAnimation {
                    id: temperatureAnimationCold1
                    target: temperatureGradientStop
                    property: "color"
                    to: "#294663"
                    duration: 10000
                    running: mug.temperatureType == Mug.TemperatureType.Cold && window.overlayMode
                }

                PropertyAnimation {
                    id: temperatureAnimationWarm2
                    target: temperatureGradientStart
                    property: "color"
                    to: "#873746"
                    duration: 10000
                    running: mug.temperatureType == Mug.TemperatureType.Warm && window.overlayMode
                }

                PropertyAnimation {
                    id: temperatureAnimationWarm1
                    target: temperatureGradientStop
                    property: "color"
                    to: "#8D6F3E"
                    duration: 10000
                    running: mug.temperatureType == Mug.TemperatureType.Warm && window.overlayMode
                }

                PropertyAnimation {
                    id: temperatureAnimationHot2
                    target: temperatureGradientStart
                    property: "color"
                    to: "#ff5858"
                    duration: 10000
                    running: mug.temperatureType == Mug.TemperatureType.Hot && window.overlayMode
                }

                PropertyAnimation {
                    id: temperatureAnimationHot1
                    target: temperatureGradientStop
                    property: "color"
                    to: "#f09819"
                    duration: 10000
                    running: mug.temperatureType == Mug.TemperatureType.Hot && window.overlayMode
                }
            }

            BusyIndicator {
                id: busyIndicator
                anchors.verticalCenter: parent.verticalCenter
                visible: temperatureText.text == ""
                Component.onCompleted: {
                    contentItem.pen = "white"
                    contentItem.fill = "white"
                }
                anchors.verticalCenterOffset: 0
                anchors.horizontalCenterOffset: 2
                anchors.horizontalCenter: parent.horizontalCenter
            }

        }

        Rectangle {
            id: bottombar
            visible: !window.overlayMode
            height: 40
            color: "#00000000"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.leftMargin: 0
            anchors.rightMargin: 0

            PropertyAnimation {
                id: animationMenu
                target: bottombar
                property: "anchors.bottomMargin"
                to: if(bottombar.anchors.bottomMargin == 40) return 0; else return 40;
                duration: 200
                easing.type: Easing.InOutQuint
            }

            CustomBtn {
                id: expand
                anchors.fill: parent
                enabled: false
                anchors.rightMargin: 0
                anchors.bottomMargin: 0
                anchors.leftMargin: 0
                anchors.topMargin: 0
                autoRepeat: false
                iconSource: if(bottombar.anchors.bottomMargin == 40) return "SVGs/chevron-down.png"; else return "SVGs/chevron-up.png";
                flat: false
                onClicked: animationMenu.running = true

                Row {
                    id: presets
                    x: -8
                    y: 40
                    height: 41
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    rightPadding: 20
                    leftPadding: 20
                    spacing: 70
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0
                    anchors.bottomMargin: -41

                    CustomBtn {
                        id: coffeeBtn
                        iconSource: "SVGs/coffee-outline.png"
                        display: AbstractButton.IconOnly
                        onClicked: backend.set_coffee()
                    }

                    CustomBtn {
                        id: button1
                        text: qsTr("Button")
                        iconSource: "SVGs/tea-outline.png"
                        display: AbstractButton.IconOnly
                        onClicked: backend.set_tea()
                    }

                    CustomBtn {
                        id: button2
                        width: 40
                        height: 40
                        text: qsTr("Button")
                        iconSource: "SVGs/thermometer-plus.png"
                        display: AbstractButton.IconOnly
                        onClicked: internal.showSettings()
                    }
                }
            }
        }
    }

    DropShadow {
        visible: false
        anchors.fill: background
        horizontalOffset: 0
        verticalOffset: 0
        radius: 10
        samples: 16
        color: "#80000000"
        source: background
        z: 0
    }

    Connections{
        target: backend

        //function to disable buttons when no mug is connected
        //Still needs to automatically hide or kill the settings window.
        function onConnectionChanged(connected){
            if(connected){
                busyIndicator.visible = false
                expand.enabled = true
                coffeeBtn.enabled = true
                button1.enabled = true
                button2.enabled = true
            }else{
                expand.enabled = false
                coffeeBtn.enabled = false
                button1.enabled = false
                button2.enabled = false
                mug.reset()
            }
        }

        function onGetDegree(degree) {
            mug.temperature = degree

            if (degree > 53.0) {
                mug.temperatureType = Mug.TemperatureType.Hot
            } else if(degree > 40.0) {
                mug.temperatureType = Mug.TemperatureType.Warm
            } else {
                mug.temperatureType = Mug.TemperatureType.Cold
            }
        }

        function onGetBattery(battery, charging) {
            mug.batteryCharge = battery
            mug.charging = charging
        }
    }

}

/*##^##
Designer {
    D{i:0;formeditorZoom:1.66}
}
##^##*/
