import QtQuick 2.15

QtObject {
    id: mug
    enum TemperatureType {
        Cold,
        Warm,
        Hot
    }

    property real temperature: -1.0
    property int temperatureType: Mug.TemperatureType.Cold
    property real batteryCharge: -1.0
    property bool charging: false

    function reset() {
        mug.temperature = -1.0
        mug.temperatureType = Mug.TemperatureType.Cold
        mug.batteryCharge = -1.0
        mug.charging = false
    }
}