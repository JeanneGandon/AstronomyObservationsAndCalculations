# Solar Spectroscopy
# Loading and Displaying the 2d Image Data
#The first steps are to load in our data.  We'll have to specify where our data are located.
#For a first step, let's locate the data directory, specify a sample file and display its image.

data_dir = '/data/home/a180u/' # EDIT this to reflect correct path to data files
im_fn = '14255654-2022-10-04-154848.fits'

from astropy.io import fits  # this library provides interaction to FITS files
im = fits.getdata(data_dir+im_fn) # this loads the image data from our FITS file into a variable

# Set up a figure and axes
fig = pylab.figure() # creates a Figure object, onto which we can put different sets of coordinate axes
ax = fig.add_subplot(111) # we'll create an Axes object, just one instance for this figure (this syntax is arcane, ignore for now)

# Now let's generate a display of our image data onto the Axes object
ax.imshow(im) # the imshow() command displays 2d arrays of data

pylab.show() # This will show the figure on the screen.


#Let's look at the above to see which rows have good data.  Since the Sun might not cover the whole slit, or the slit might be blocked on one side, or the image is off the detector, we might not get good data on all rows.  (That said, maybe you do!)
#Suppose rows 100 to 300 were good.  We could create a new array that had only those rows through the process of indexing, `im[100:300, :]`.  This says give us rows 100 to 300, and all columns.

# FIXME  change these rows to match your own data.  
im = im[200:300, :]  # use indexing to get a subset of the original array

fig = pylab.figure() # creates a new Figure object
ax = fig.add_subplot(111) # create a new Axes object
ax.imshow(im) # display our new subarray
pylab.show()


## Reducing the Image to a 1d Spectrum
#Now we'll create a 1-dimensional array by collapsing the valid rows. We will use the `sum()` method which adds together the specified data along the specified dimension (a.k.a. "axis" in numpy-speak).

spectrum = im.sum(axis=0) # sum over all the rows to get the spectrum
print(spectrum.shape) # check the dimensionality of the spectrum

#Note that the spectrum is one dimensional, with 640 elements (the x size of the detector).
#It is helpful for plotting and fitting to define a one-dimensional array containing the array index. First we find the size of the spectrum image and then make a 1-d index array.  We can then construct a graph of the two absorption features. 

x = np.arange(len(spectrum)) # this gives us an array of indices

fig = pylab.figure()
ax = fig.add_subplot(111)

# let's plot the entire spectrum 
ax.plot(x, spectrum)

# and show it
pylab.draw()

#Hopefully we can see two absorption lines!

## Fitting for an individual line
#What we need is to fit a Gaussian to each line individually in order to measure the center of each line's position. To do this use the plot of the complete spectrum to roughly identify the center pixel. Let's pick the line on the left, and say it's roughly at $x=170$. We can zoom in on that line by plotting only a subrange of the spectrum. The `x` variable works like an index to keep the $x$ axis correct.

fig = pylab.figure()
ax = fig.add_subplot(111)

# let's plot the subrange of the spectrum 
ax.plot(x[180:280], spectrum[180:280])

# and show it
pylab.draw()

#Next we want to use a routine being provided that fits the position of the absorption line.  It is called `fit_abs_line()`.  Again, the `x` variable is used to index the array so the values returned are for pixel locations in the original spectrum.

import sys; sys.path.append('/home/a180i/lib/python/') # this is a temporary workaround to access the a180 module
import a180 # import the module of routines for this class

# let's perform the fit of the absorption line
fy, params = a180.fit_abs_line(x[180:280], spectrum[180:280])

# Use the help feature to read more on what fit_abs_line() does. 
help(a180.fit_abs_line)

#In this usage we are fitting the data from elements 140 to 200 to a quadratic background plus a Gaussian. If we print the `params` array, it contains the coefficients of the fit.

print(params)

#The `params[0]` element (which is the first one listed) is the center of the Gaussian. The routine also produces an array `fy` which is the best fit function evaluated at the $x$ locations in `x[140:200]`. You can overplot this fit on top of the data. You'll again need to use the `x` variable to keep the pixel locations straight:

fig = pylab.figure()
ax = fig.add_subplot(111)

ax.plot(x[180:280], spectrum[180:280])  # let's plot the subrange of the spectrum 
ax.plot(x[180:280], fy) # and also our best-fit curve
ax.axvline(params[0]) # mark a vertical line at the best-fit position

# and show it
pylab.draw()

#Check that the `fy` model is a good fit to the data. If so, we should record the `params[0]` element as the position of the line you we're examining.

#We need to repeat this procedure for the right-side spectral line.  And we need to do it for all images in our dataset.

## Application to several exposures

#Let's look at a structure for doing the left-side lines on an entire list of files.


# let's define a list of filenames.  This should be a list of exposures on one limb of the Sun.  We'll need to repeat this on the other limb.
fns = ['14255654-2022-10-04-154848.fits',
       '14255654-2022-10-04-154908.fits',
       '14255654-2022-10-04-154913.fits',
       '14255654-2022-10-04-154919.fits',
       '14255654-2022-10-04-154923.fits'
      ]

# let's run a loop over the filenames
left_pos = [] # an empty list to store our best-fit results
right_pos = []
for fn in fns:
    # load the data
    print(data_dir+fn)
    im = fits.getdata(data_dir+fn) # load from disk
    im = im[200:300, :] # get the good rows
    spectrum = im.sum(axis=0) # compute the 1d spectrum

    # get the line fit for the left side
    fyl, paramsl = a180.fit_abs_line(x[180:280], spectrum[180:280])
    left_pos.append(paramsl[0]) # store the best-fit position 

    # get the line fit for the right side
    fy2, params2 = a180.fit_abs_line(x[400:500], spectrum[400:500])
    right_pos.append(params2[0]) # store the best-fit position 

    # set up a plot for left and right sides
    fig = pylab.figure()
    ax1 = fig.add_subplot(121) # left-side axes
    ax2 = fig.add_subplot(122) # right-side axes
    
    # display the left-side results
    ax1.plot(x[180:280], spectrum[180:280])
    ax1.plot(x[180:280], fyl)
    ax1.axvline(paramsl[0])
    ax1.set_title(fn+' - left') # title the plot

    # display the right-side results
    ax2.plot(x[400:500], spectrum[400:500])
    ax2.plot(x[400:500], fy2)
    ax2.axvline(params2[0])
    ax2.set_title(fn+' - right') # title the plot
    # show the plot
    pylab.draw()

left_pos = np.array(left_pos) # convert the list to a 1-d numpy array
right_pos = np.array(right_pos)


#Now lets examine the mean and standard deviation of our measured positions.

print('left:', left_pos.mean(), left_pos.std())
print('right:', right_pos.mean(), right_pos.std())

#Note we have measurements for one limb of the Sun.  We need measurements from the other limb of the Sun as well.

# let's define a list of filenames.  This should be a list of exposures on one limb of the Sun.  We'll need to repeat this on the other limb.
fns = [ '14255654-2022-10-04-155148.fits', 
       '14255654-2022-10-04-155154.fits', 
       '14255654-2022-10-04-155159.fits', 
       '14255654-2022-10-04-155218.fits',
       '14255654-2022-10-04-155224.fits', ]

# let's run a loop over the filenames
left_pos = [] # an empty list to store our best-fit results
right_pos = []
for fn in fns:
    # load the data
    print(data_dir+fn)
    im = fits.getdata(data_dir+fn) # load from disk
    im = im[300:400, :] # get the good rows
    spectrum = im.sum(axis=0) # compute the 1d spectrum

    # get the line fit for the left side
    fyl, paramsl = a180.fit_abs_line(x[200:300], spectrum[200:300])
    left_pos.append(paramsl[0]) # store the best-fit position 

    # get the line fit for the right side
    fy2, params2 = a180.fit_abs_line(x[400:500], spectrum[400:500])
    right_pos.append(params2[0]) # store the best-fit position 

    # set up a plot for left and right sides
    fig = pylab.figure()
    ax1 = fig.add_subplot(121) # left-side axes
    ax2 = fig.add_subplot(122) # right-side axes
    
    # display the left-side results
    ax1.plot(x[200:300], spectrum[200:300])
    ax1.plot(x[200:300], fyl)
    ax1.axvline(paramsl[0])
    ax1.set_title(fn+' - left') # title the plot

    # display the right-side results
    ax2.plot(x[400:500], spectrum[400:500])
    ax2.plot(x[400:500], fy2)
    ax2.axvline(params2[0])
    ax2.set_title(fn+' - right') # title the plot
    # show the plot
    pylab.draw()

left_pos = np.array(left_pos) # convert the list to a 1-d numpy array
right_pos = np.array(right_pos)

print('left:', left_pos.mean(), left_pos.std())
print('right:', right_pos.mean(), right_pos.std())

## Computing the rotation rate

#These steps follow the steps in your lab handout.  Don't forget to follow your uncertainties!

# 1. Estimate the wavelength scale
realwavediff=589.59236-588.99504
rightlimbdiff=454.418895825389-229.24758457334033
leftlimbdiff=461.78301417047913-236.6075156110211
rightscale=realwavediff/rightlimbdiff
leftscale=realwavediff/leftlimbdiff
averagescale=(rightscale+leftscale)/2
print (leftlimbdiff,'Left Limb difference')
print (rightlimbdiff, 'Right Limb difference')
print (averagescale,'average scale of both limbs in nm/pixel')

# 2a. Calculate the observed Doppler shift in nm
rightlimblower=229.24758457334033
rightlimbupper=454.418895825389
leftlimblower=236.6075156110211
leftlimbupper=461.78301417047913
differencelowerline=leftlimblower-rightlimblower
differenceupperline=leftlimbupper-rightlimbupper
averagedifference=(differencelowerline+differenceupperline)/2
dopplershift=averagedifference
dopplershiftnm=dopplershift*averagescale
print (dopplershiftnm,'observed doppler shift in nm')

# 2b. Calculate the observed Doppler shift in velocity
restwavelength1=588.99504
restwavelength2=589.59236
c=3*(10**17) #in nm/s
v1=(c*dopplershiftnm)/restwavelength1
v2=(c*dopplershiftnm)/restwavelength2
v1ms=v1*(10**-9)
v2ms=v2*(10**-9)
averagev=(v1ms+v2ms)/2
print('doppler shift in velocity',averagev,'m/s')

# 3. Correct for the axial tilt of the Sun

tilt=np.cos(26.14)
newv=tilt*averagev
print(newv, 'axial tilt corrected velocity m/s')

# 4. Correct for the position of the slit relative to the limb

truev=newv*.9

# 5. Correct for the rotation of the solar image on the slit plane

truetruev=np.sin(20)*truev

# 6+7. Compute the Solar equatorial rotation rate 

equatorialv=truetruev/2
print(equatorialv,'m/s solar equatorial rotation rate')

## Physical size of the Sun

# compute the radius of the Sun in km
earthday=365.34
T=25 
TC= ( ((earthday**2)+4*T*earthday)**.5- earthday ) /2
print(TC)
S=1954.186356925
RT=TC*86400
RTS=RT*S
radius=RTS/ (2*np.pi) 
radiussun=radius/1000
print (radiussun, 'km, radius of the Sun')

## Mass of the Sun

# Compute the distance to the Sun

siderealday=23.93*60 
rad=2*np. pi
rads=rad/siderealday 
degs=rads*57.2958
crossingtime=2.04 
angle=degs*crossingtime
dtosun=57.2958*2*radiussun/angle
print(dtosun,'km distance to sun')

# Compute the Mass of the Sun

circumference=2*np.pi*dtosun
secondsaround=365.34*86400
vearth=circumference/secondsaround
print (vearth,'km/s velocity of Earth around Sun')

mass= (dtosun*1000)*((vearth*1000)**2)/(6.67*10**-11)
print (mass, 'Mass of Sun in Kg')