import QtQuick
import Quickshell
import Quickshell.Io

Item {
  id: root
  property var bar
  property string pointer: Quickshell.env("HUMAIN_POINTER") || "https://buildinpublicuniversity.com/"
  property string resolutionState: "unavailable"
  property string host: "public pointer"
  property string detail: "Adapter unavailable"

  implicitWidth: 90
  implicitHeight: bar ? bar.barSize : 26

  function refresh() {
    if (!resolveProc.running) resolveProc.running = true
  }

  Process {
    id: resolveProc
    command: [
      "curl", "-fsS", "--max-time", "3",
      "-X", "POST", "http://127.0.0.1:8787/v1/context",
      "-H", "Content-Type: application/json",
      "--data-binary", JSON.stringify({pointer: root.pointer, requester: "omarchy-quickshell"})
    ]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try {
          var parsed = JSON.parse(String(text || "").trim())
          root.resolutionState = parsed.resolution_state || "unavailable"
          root.host = (parsed.payload && parsed.payload.host) || "public pointer"
          root.detail = root.resolutionState === "public_only" ? "Public pointer only" : "Unavailable"
        } catch (error) {
          root.resolutionState = "unavailable"
          root.detail = "Adapter unavailable"
        }
      }
    }
    onExited: function(exitCode) {
      if (exitCode !== 0) {
        root.resolutionState = "unavailable"
        root.detail = "Adapter unavailable"
      }
    }
  }

  Timer {
    interval: 30000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  Text {
    anchors.centerIn: parent
    text: root.resolutionState === "public_only" ? "◉ HumAIn" : "⊘ HumAIn"
    color: root.bar ? root.bar.foreground : "white"
    font.family: root.bar ? root.bar.fontFamily : "monospace"
    font.pixelSize: 13
  }

  MouseArea {
    anchors.fill: parent
    onClicked: root.refresh()
  }
}
