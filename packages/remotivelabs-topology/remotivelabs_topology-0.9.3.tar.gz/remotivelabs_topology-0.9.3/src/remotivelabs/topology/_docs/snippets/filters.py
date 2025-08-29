from remotivelabs.topology.namespaces.filters import AllFramesFilter, FrameFilter

filters1 = [
    AllFramesFilter(),
    FrameFilter(frame_name="Frame1", include=False),
]
filters2 = [
    FrameFilter(frame_name="Frame1", include=False),
    AllFramesFilter(),
]
