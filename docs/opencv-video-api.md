Help on class VideoCapture in module cv2:

class VideoCapture(builtins.object)
 |  Methods defined here:
 |
 |  __init__(self, /, *args, **kwargs)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __repr__(self, /)
 |      Return repr(self).
 |
 |  get(...)
 |      get(propId) -> retval
 |      .   @brief Returns the specified VideoCapture property
 |      .
 |      .       @param propId Property identifier from cv::VideoCaptureProperties (eg. cv::CAP_PROP_POS_MSEC, cv::CAP_PROP_POS_FRAMES, ...)
 |      .       or one from @ref videoio_flags_others
 |      .       @return Value for the specified property. Value 0 is returned when querying a property that is
 |      .       not supported by the backend used by the VideoCapture instance.
 |      .
 |      .       @note Reading / writing properties involves many layers. Some unexpected result might happens
 |      .       along this chain.
 |      .       @code{.txt}
 |      .       VideoCapture -> API Backend -> Operating System -> Device Driver -> Device Hardware
 |      .       @endcode
 |      .       The returned value might be different from what really used by the device or it could be encoded
 |      .       using device dependent rules (eg. steps or percentage). Effective behaviour depends from device
 |      .       driver and API Backend
 |
 |  getBackendName(...)
 |      getBackendName() -> retval
 |      .   @brief Returns used backend API name
 |      .
 |      .        @note Stream should be opened.
 |
 |  getExceptionMode(...)
 |      getExceptionMode() -> retval
 |      .
 |
 |  grab(...)
 |      grab() -> retval
 |      .   @brief Grabs the next frame from video file or capturing device.
 |      .
 |      .       @return `true` (non-zero) in the case of success.
 |      .
 |      .       The method/function grabs the next frame from video file or camera and returns true (non-zero) in
 |      .       the case of success.
 |      .
 |      .       The primary use of the function is in multi-camera environments, especially when the cameras do not
 |      .       have hardware synchronization. That is, you call VideoCapture::grab() for each camera and after that
 |      .       call the slower method VideoCapture::retrieve() to decode and get frame from each camera. This way
 |      .       the overhead on demosaicing or motion jpeg decompression etc. is eliminated and the retrieved frames
 |      .       from different cameras will be closer in time.
 |      .
 |      .       Also, when a connected camera is multi-head (for example, a stereo camera or a Kinect device), the
 |      .       correct way of retrieving data from it is to call VideoCapture::grab() first and then call
 |      .       VideoCapture::retrieve() one or more times with different values of the channel parameter.
 |      .
 |      .       @ref tutorial_kinect_openni
 |
 |  isOpened(...)
 |      isOpened() -> retval
 |      .   @brief Returns true if video capturing has been initialized already.
 |      .
 |      .       If the previous call to VideoCapture constructor or VideoCapture::open() succeeded, the method returns
 |      .       true.
 |
 |  open(...)
 |      open(filename[, apiPreference]) -> retval
 |      .   @brief  Opens a video file or a capturing device or an IP video stream for video capturing.
 |      .
 |      .       @overload
 |      .
 |      .       Parameters are same as the constructor VideoCapture(const String& filename, int apiPreference = CAP_ANY)
 |      .       @return `true` if the file has been successfully opened
 |      .
 |      .       The method first calls VideoCapture::release to close the already opened file or camera.
 |
 |
 |
 |      open(filename, apiPreference, params) -> retval
 |      .   @brief  Opens a video file or a capturing device or an IP video stream for video capturing with API Preference and parameters
 |      .
 |      .       @overload
 |      .
 |      .       The `params` parameter allows to specify extra parameters encoded as pairs `(paramId_1, paramValue_1, paramId_2, paramValue_2, ...)`.
 |      .       See cv::VideoCaptureProperties
 |      .
 |      .       @return `true` if the file has been successfully opened
 |      .
 |      .       The method first calls VideoCapture::release to close the already opened file or camera.
 |
 |
 |
 |      open(index[, apiPreference]) -> retval
 |      .   @brief  Opens a camera for video capturing
 |      .
 |      .       @overload
 |      .
 |      .       Parameters are same as the constructor VideoCapture(int index, int apiPreference = CAP_ANY)
 |      .       @return `true` if the camera has been successfully opened.
 |      .
 |      .       The method first calls VideoCapture::release to close the already opened file or camera.
 |
 |
 |
 |      open(index, apiPreference, params) -> retval
 |      .   @brief  Opens a camera for video capturing with API Preference and parameters
 |      .
 |      .       @overload
 |      .
 |      .       The `params` parameter allows to specify extra parameters encoded as pairs `(paramId_1, paramValue_1, paramId_2, paramValue_2, ...)`.
 |      .       See cv::VideoCaptureProperties
 |      .
 |      .       @return `true` if the camera has been successfully opened.
 |      .
 |      .       The method first calls VideoCapture::release to close the already opened file or camera.
 |
 |
 |
 |      open(source, apiPreference, params) -> retval
 |      .   @brief Opens a video using data stream.
 |      .
 |      .       @overload
 |      .
 |      .       The `params` parameter allows to specify extra parameters encoded as pairs `(paramId_1, paramValue_1, paramId_2, paramValue_2, ...)`.
 |      .       See cv::VideoCaptureProperties
 |      .
 |      .       @return `true` if the file has been successfully opened
 |      .
 |      .       The method first calls VideoCapture::release to close the already opened file or camera.
 |
 |  read(...)
 |      read([, image]) -> retval, image
 |      .   @brief Grabs, decodes and returns the next video frame.
 |      .
 |      .       @param [out] image the video frame is returned here. If no frames has been grabbed the image will be empty.
 |      .       @return `false` if no frames has been grabbed
 |      .
 |      .       The method/function combines VideoCapture::grab() and VideoCapture::retrieve() in one call. This is the
 |      .       most convenient method for reading video files or capturing data from decode and returns the just
 |      .       grabbed frame. If no frames has been grabbed (camera has been disconnected, or there are no more
 |      .       frames in video file), the method returns false and the function returns empty image (with %cv::Mat, test it with Mat::empty()).
 |      .
 |      .       @note In @ref videoio_c "C API", functions cvRetrieveFrame() and cv.RetrieveFrame() return image stored inside the video
 |      .       capturing structure. It is not allowed to modify or release the image! You can copy the frame using
 |      .       cvCloneImage and then do whatever you want with the copy.
 |
 |  release(...)
 |      release() -> None
 |      .   @brief Closes video file or capturing device.
 |      .
 |      .       The method is automatically called by subsequent VideoCapture::open and by VideoCapture
 |      .       destructor.
 |      .
 |      .       The C function also deallocates memory and clears \*capture pointer.
 |
 |  retrieve(...)
 |      retrieve([, image[, flag]]) -> retval, image
 |      .   @brief Decodes and returns the grabbed video frame.
 |      .
 |      .       @param [out] image the video frame is returned here. If no frames has been grabbed the image will be empty.
 |      .       @param flag it could be a frame index or a driver specific flag
 |      .       @return `false` if no frames has been grabbed
 |      .
 |      .       The method decodes and returns the just grabbed frame. If no frames has been grabbed
 |      .       (camera has been disconnected, or there are no more frames in video file), the method returns false
 |      .       and the function returns an empty image (with %cv::Mat, test it with Mat::empty()).
 |      .
 |      .       @sa read()
 |      .
 |      .       @note In @ref videoio_c "C API", functions cvRetrieveFrame() and cv.RetrieveFrame() return image stored inside the video
 |      .       capturing structure. It is not allowed to modify or release the image! You can copy the frame using
 |      .       cvCloneImage and then do whatever you want with the copy.
 |
 |  set(...)
 |      set(propId, value) -> retval
 |      .   @brief Sets a property in the VideoCapture.
 |      .
 |      .       @param propId Property identifier from cv::VideoCaptureProperties (eg. cv::CAP_PROP_POS_MSEC, cv::CAP_PROP_POS_FRAMES, ...)
 |      .       or one from @ref videoio_flags_others
 |      .       @param value Value of the property.
 |      .       @return `true` if the property is supported by backend used by the VideoCapture instance.
 |      .       @note Even if it returns `true` this doesn't ensure that the property
 |      .       value has been accepted by the capture device. See note in VideoCapture::get()
 |
 |  setExceptionMode(...)
 |      setExceptionMode(enable) -> None
 |      .   Switches exceptions mode
 |      .        *
 |      .        * methods raise exceptions if not successful instead of returning an error code
 |
 |  ----------------------------------------------------------------------
 |  Static methods defined here:
 |
 |  __new__(*args, **kwargs)
 |      Create and return a new object.  See help(type) for accurate signature.
 |
 |  waitAny(...)
 |      waitAny(streams[, timeoutNs]) -> retval, readyIndex
 |      .   @brief Wait for ready frames from VideoCapture.
 |      .
 |      .       @param streams input video streams
 |      .       @param readyIndex stream indexes with grabbed frames (ready to use .retrieve() to fetch actual frame)
 |      .       @param timeoutNs number of nanoseconds (0 - infinite)
 |      .       @return `true` if streamReady is not empty
 |      .
 |      .       @throws Exception %Exception on stream errors (check .isOpened() to filter out malformed streams) or VideoCapture type is not supported
 |      .
 |      .       The primary use of the function is in multi-camera environments.
 |      .       The method fills the ready state vector, grabs video frame, if camera is ready.
 |      .
 |      .       After this call use VideoCapture::retrieve() to decode and fetch frame data.

