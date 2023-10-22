import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Button {
    id: smallMenuBtn
    // Custom Property
    property url iconSource: "../SVGs/chevron-up.svg"
    property color btnColorDefault: "#00000000"
    property color btnColorMouseOver: "#23272E"

    QtObject {
        id: internal
        property var dynamicColor: smallMenuBtn.hovered? btnColorMouseOver : btnColorDefault
    }
    width: 16
    height: 16

    background: buttonBackground
    Rectangle {
        id: buttonBackground
        color: internal.dynamicColor
        border.color: "#00000000"

        Image {
            id: iconBtn
            source: iconSource
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 16
            width: 16
            antialiasing: false
            fillMode: Image.PreserveAspectFit
        }
    }
}



/*##^##
Designer {
    D{i:0;height:16;width:16}
}
##^##*/
