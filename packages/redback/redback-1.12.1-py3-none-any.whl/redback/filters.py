from astropy.io import ascii
from astropy import units as u
from astroquery.svo_fps import SvoFps
import numpy as np
from redback.utils import calc_effective_width_hz_from_angstrom
import redback
import sncosmo

def add_to_database(label, wavelength, zeroflux, database, plot_label, effective_width):

    """
    Add a filter to the Redback filter database.

    :param label:       name of the filter in the Redback filter database
    :param wavelength:  central wavelength of the filter as defined on SVO in m
    :param zeroflux:   zero flux of the filter in erg/cm^2/s/Hz
    :param database:    filter database
    :param plot_label:  plot label. If none is provided, it will use LABEL (default: None).
    :param effective_width: effective width of the filter in Angstrom
    :return: None
    """

    frequency = 3.0e8 / wavelength
    effective_width = calc_effective_width_hz_from_angstrom(effective_width=effective_width,
                                                            effective_wavelength=wavelength * 1e10)
    database.add_row([label, frequency, wavelength * 1e10, 'black', zeroflux, label, plot_label, effective_width])

def add_to_sncosmo(label, transmission):

    """
    Add a filter to the Redback filter database.

    :param label:       name of the filter in the Redback filter database
    :param WAVELENGTH:  central wavelength of the filter as defined on SVO
    :return: None
    """

    band  = sncosmo.Bandpass(transmission['Wavelength'], transmission['Transmission'], name=label, wave_unit=u.angstrom)
    sncosmo.register(band, label, force=True)

def add_filter_svo(filter, label, plot_label=None, overwrite=False):

    """
    Wrapper to add a filter from SVO to SNCosmo and the Redback filter database

    :param filter: record from the SVO query
    :param label:  name of the filter in SNCosmo
    :param plot_label: plot label. If none is provided, it will use LABEL (default: None).
    :param overwrite:  overwrite any existing entry? (default: False)
    :return: None
    """

    redback_db_fname = redback.__path__[0] + '/tables/filters.csv'
    database_filters = ascii.read(redback_db_fname)
    
    mask = np.where((database_filters['bands'] == label) & (database_filters['sncosmo_name'] == label))[0]
    
    # Only add filter to filter database if entry does not exist in the Redback database by default
    
    # If no entry exists or you choose to overwrite an entry
    if (len(mask) == 0) or ((len(mask) != 0) & overwrite):

        if len(mask) > 0:
            database_filters.remove_rows(mask)

        # Reference (=pivot) wavelength, unit: AA
        wavelength_pivot = filter['WavelengthRef']

        # Effective width
        # defined as int( T(lambda), lambda ) / max( T(lambda) ), unit: AA
        effective_width  = filter['WidthEff']

        # Zero flux

        ## Motivation:
        ## Filters have a width. X-ray astronomy work in flux not flux density. To combine
        ## observations from different parts of the EM spectrum, we need to be able to
        ## convert Fnu to F.
        
        ## Solution: We use the effective width to convert Fnu to F.

        constant   = 3631e-23*3e8*1e10 # AB mag ZP (erg/cm^2/s/Hz) x light speed (m/s) * wavelength (m)
        zeroflux   = constant * ( 1 / (wavelength_pivot - effective_width/2.) - 1 / (wavelength_pivot + effective_width/2.) )

        # Add to Redback

        plot_label = plot_label if plot_label != None else label

        add_to_database(label, wavelength_pivot * 1.0e-10, zeroflux, database_filters, plot_label, effective_width)

    # Non-standard filters always needs to be re-added to SN Cosmo even if an entry exists in filter.csv

    filter_transmission = SvoFps.get_transmission_data(filter['filterID'])
    add_to_sncosmo(label, filter_transmission)

    # Prettify output

    database_filters['wavelength [Hz]'].info.format = '.05e'
    database_filters['wavelength [Angstrom]'].info.format = '.05f'
    database_filters['reference_flux'].info.format = '.05e'
    database_filters['effective_width [Hz]'].info.format = '.05e'

    database_filters.write(redback_db_fname, overwrite=True, format='csv')

def add_filter_user(file, label, plot_label=None, overwrite=False):

    """
    Wrapper to add a user filter from SVO to SNCosmo and the Redback filter database
    :param file:       file name that contains the transmission function
                       (Must have two columns, wavelength must be in AA)
    :param label:      name of the filter
    :param DATABASE:   location of the Redback filter database
    :param plot_label: plot label. If none is provided, it will use LABEL (default: None).
    :param overwrite:  overwrite any existing entry? (default: False)
    :return: None
    """

    # Read Redback filter database

    redback_db_fname = path = redback.__path__[0] + '/tables/filters.csv'
    database_filters = ascii.read(redback_db_fname)

    # Check whether such an entry already exists
    mask = np.where((database_filters['bands'] == label) & (database_filters['sncosmo_name'] == label))[0]

    # Add to SNCosmo
    # Needs to be done even if an entry exists in filters.csv

    filter_transmission = ascii.read(file)
    filter_transmission.rename_columns(list(filter_transmission.keys()), ['Wavelength', 'Transmission'])

    add_to_sncosmo(label, filter_transmission)

    # Add to filter.csv

    # If no entry exists or you choose to overwrite an entry

    if (len(mask) == 0) or ((len(mask) != 0) & overwrite):
        
        if len(mask) > 0:
            database_filters.remove_rows(mask)

        # Central wavelength as defined on SVO
        # int(T*l, dl) / int(T, dl)
        # unit: AA
        
        wavelength_pivot  = np.trapz(filter_transmission['Wavelength'] * filter_transmission['Transmission'], filter_transmission['Wavelength'])
        wavelength_pivot /= np.trapz(filter_transmission['Transmission'], filter_transmission['Wavelength'])
        
        # Effective width as defined on SVO
        # int( T(lambda), lambda ) / max( T(lambda) )
        # unit: AA
        effective_width = np.trapz(filter_transmission['Transmission'], filter_transmission['Wavelength']) / max(filter_transmission['Transmission'])

        # Zero flux

        ## Motivation:
        ## Filters have a width. X-ray astronomy work in flux not flux density. To combine
        ## observations from different parts of the EM spectrum, we need to be able to
        ## convert Fnu to F.
        
        ## Solution: We use the effective width to convert Fnu to F.

        constant   = 3631e-23*3e8*1e10 # AB mag ZP (erg/cm^2/s/Hz) x light speed (m/s) * wavelength (m)
        zeroflux   = constant * ( 1 / (wavelength_pivot - effective_width/2.) - 1 / (wavelength_pivot + effective_width/2.) )

        # Add to Redback
        
        plot_label = plot_label if plot_label != None else label

        print(label, wavelength_pivot * 1.0e-10, zeroflux, plot_label)

        add_to_database(label, wavelength_pivot * 1.0e-10, zeroflux, database_filters, plot_label, effective_width)

        # Prettify output

        database_filters['wavelength [Hz]'].info.format = '.05e'
        database_filters['wavelength [Angstrom]'].info.format = '.05f'
        database_filters['reference_flux'].info.format = '.05e'
        database_filters['effective_width [Hz]'].info.format = '.05e'

        database_filters.write(redback_db_fname, overwrite=True, format='csv')
    
    else:
        
        print('Filter {} already exists. Set OVERWRITE to True if you want to overwrite the existing entry'.format(label))

def add_common_filters(overwrite=False):

    """
    Adds Euclid, NTT/EFOSC2, MPG/GROND, Spitzer and WISE filters from SVO

    :return: None
    """

    # GROND

    print('MPG/GROND optical and NIR filters...')

    filter_list  = SvoFps.get_filter_list(facility='La Silla', instrument='GROND')
    filter_label = ['grond::' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]
    plot_label   = ['GROND/' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]

    [add_filter_svo(filter_list[ii], filter_label[ii], plot_label[ii], overwrite=overwrite) for ii in range(len(filter_list))]

    print('done.\n')

    # NTT/EFOSC2
    # Adding only Gunn filters

    print('NTT/EFOSC2 Gunn filters...')

    filter_list  = SvoFps.get_filter_list(facility='La Silla', instrument='EFOSC')
    mask         = [True if ('Gunn' in filter_list['Description'][ii]) else False for ii in range(len(filter_list))]
    filter_list  = filter_list[mask]
    filter_label = ['efosc2::' + x for x in filter_list['Band']]
    plot_label   = ['EFOSC/' + x for x in filter_list['Band']]

    [add_filter_svo(filter_list[ii], filter_label[ii], plot_label[ii], overwrite=overwrite) for ii in range(len(filter_list))]

    print('done.\n')

    # Euclid

    print('EUCLID optical and IR filters...')

    filter_list  = SvoFps.get_filter_list(facility='Euclid', instrument='VIS')
    filter_label = ['euclid::' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]
    plot_label   = ['EUCLID/' + x.split('/')[1].split('.')[1].upper() for x in filter_list['filterID']]

    [add_filter_svo(filter_list[ii], filter_label[ii], plot_label[ii], overwrite=overwrite) for ii in range(len(filter_list))]


    filter_list  = SvoFps.get_filter_list(facility='Euclid', instrument='NISP')
    mask         = [True if 'NISP.' in filter_list['filterID'][ii] else False for ii in range(len(filter_list))]
    filter_list  = filter_list[mask]
    filter_label = ['euclid::' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]
    plot_label   = ['EUCLID/' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]

    [add_filter_svo(filter_list[ii], filter_label[ii], plot_label[ii], overwrite=overwrite) for ii in range(len(filter_list))]

    print('done.\n')

    # Spitzer

    print('Spitzer IRAC filters...')

    filter_list  = SvoFps.get_filter_list(facility='Spitzer', instrument='IRAC')
    filter_label = ['irac::' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]
    plot_label   = ['IRAC/' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]

    [add_filter_svo(filter_list[ii], filter_label[ii], plot_label[ii], overwrite=overwrite) for ii in range(len(filter_list))]

    print('done.\n')

    # WISE

    print('WISE filters...')

    filter_list  = SvoFps.get_filter_list(facility='WISE')
    filter_label = ['wise::' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]
    plot_label   = ['WISE/' + x.split('/')[1].split('.')[1] for x in filter_list['filterID']]

    [add_filter_svo(filter_list[ii], filter_label[ii], plot_label[ii], overwrite=overwrite) for ii in range(len(filter_list))]

    print('done.\n')

def show_all_filters():

    redback_db_fname = redback.__path__[0] + '/tables/filters.csv'
    database_filters = ascii.read(redback_db_fname)
    
    return database_filters

def add_effective_widths():
    """
    Adds effective widths to the Redback filter database

    :return: None
    """
    import pandas as pd
    db = pd.read_csv(redback.__path__[0] + '/tables/filters.csv')
    import sncosmo
    eff_width = np.zeros(len(db))
    for ii, bb in enumerate(db['sncosmo_name']):
        try:
            band = sncosmo.get_bandpass(bb)
            waves = band.wave  # wavelengths in Angstroms
            trans = band.trans  # corresponding transmission values

            # Calculate the effective width:
            #   effective_width = ∫T(λ) dλ / max(T(λ))
            effective_width = np.trapz(trans, waves) / np.max(trans)
            effective_width = calc_effective_width_hz_from_angstrom(effective_width=effective_width,
                                                                    effective_wavelength=band.wave_eff)
            eff_width[ii] = effective_width
        except Exception:
            redback.utils.logger.warning("Failed for band={} at index={}".format(bb, ii))
            eff_width[ii] = db['wavelength [Hz]'].iloc[ii]

    db['effective_width [Hz]'] = eff_width
    db.to_csv(redback.__path__[0] + '/tables/filters.csv', index=False)