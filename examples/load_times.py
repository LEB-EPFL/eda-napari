with tifffile.TiffFile(filePath) as tif:
    try:
        mdInfo = tif.imagej_metadata['Info']  # pylint: disable=E1136  # pylint/issues/3139
        if mdInfo is None:
            mdInfo = tif.shaped_metadata[0]['Infos']  # pylint: disable=E1136
        mdInfoDict = json.loads(mdInfo)
        elapsedTime = mdInfoDict['ElapsedTime-ms']
    except (TypeError, KeyError) as _:
        mdInfoDict = xmltodict.parse(tif.ome_metadata, force_list={'Plane'})
        elapsedTime = float(mdInfoDict['OME']['Image']['Pixels']['Plane'][0]['@DeltaT'])


def loadTifStackElapsed(file, numFrames=None, skipFrames=0):
    """ this should ideally be added to loadElapsed """
    elapsed = []
    with tifffile.TiffFile(file) as tif:
        if numFrames is None:
            numFrames = len(tif.pages)

        try:
            mdInfo = tif.ome_metadata  # pylint: disable=E1136  # pylint/issues/3139
            # This should work for single series ome.tifs
            mdInfoDict = xmltodict.parse(mdInfo)
            for frame in range(0, numFrames):
                # Check which unit the DeltaT is
                if mdInfoDict['OME']['Image']['Pixels']['Plane'][frame]['@DeltaTUnit'] == 's':
                    unitMultiplier = 1000
                else:
                    unitMultiplier = 1
                if (frame % (skipFrames+1)) != 0:
                    continue
                elapsed.append(unitMultiplier*float(
                    mdInfoDict['OME']['Image']['Pixels']['Plane'][frame]['@DeltaT']))
        except (TypeError, KeyError):
            elapsed = np.arange(0, numFrames)
    return elapsed