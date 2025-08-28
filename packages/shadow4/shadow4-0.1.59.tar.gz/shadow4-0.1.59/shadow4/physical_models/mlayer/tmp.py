from shadow4.beamline.s4_beamline import S4Beamline

beamline = S4Beamline()

#
#
#
from shadow4.sources.source_geometrical.source_geometrical import SourceGeometrical

light_source = SourceGeometrical(name='SourceGeometrical', nrays=5000, seed=5676561)
light_source.set_spatial_type_gaussian(sigma_h=0.000402, sigma_v=0.000009)
light_source.set_depth_distribution_off()
light_source.set_angular_distribution_gaussian(sigdix=0.000013, sigdiz=0.000007)
light_source.set_energy_distribution_singleline(12400.000000, unit='eV')
light_source.set_polarization(polarization_degree=1.000000, phase_diff=0.000000, coherent_beam=0)
beam = light_source.get_beam()

beamline.set_light_source(light_source)

# optical element number XX
boundary_shape = None

from shadow4.beamline.optical_elements.multilayers.s4_ellipsoid_multilayer import S4EllipsoidMultilayer

optical_element = S4EllipsoidMultilayer(name='Ellipsoid Multilayer', boundary_shape=boundary_shape,
                                        surface_calculation=0,
                                        min_axis=2.000000, maj_axis=2.000000, pole_to_focus=1.000000,
                                        p_focus=33.500000, q_focus=1.500000, grazing_angle=0.013090,
                                        is_cylinder=1, cylinder_direction=0, convexity=1,
                                        f_refl=0, file_refl='/nobackup/gurb1/srio/Oasys/mlayer_pdb4c_graded.dat',
                                        structure='[B/W]x50+Si', period=25.000000, Gamma=0.500000)

from syned.beamline.element_coordinates import ElementCoordinates

coordinates = ElementCoordinates(p=33.5, q=1.5, angle_radial=1.557706357, angle_azimuthal=1.570796327,
                                 angle_radial_out=1.557706357)
movements = None
from shadow4.beamline.optical_elements.multilayers.s4_ellipsoid_multilayer import S4EllipsoidMultilayerElement

beamline_element = S4EllipsoidMultilayerElement(optical_element=optical_element, coordinates=coordinates,
                                                movements=movements, input_beam=beam)

beam, footprint = beamline_element.trace_beam()

beamline.append_beamline_element(beamline_element)

# test plot
if True:
    from srxraylib.plot.gol import plot_scatter

    # plot_scatter(beam.get_photon_energy_eV(nolost=1), beam.get_column(23, nolost=1), title='(Intensity,Photon Energy)',
    #              plot_histograms=0)
    # plot_scatter(1e6 * beam.get_column(1, nolost=1), 1e6 * beam.get_column(3, nolost=1), title='(X,Z) in microns')

    plot_scatter(footprint.get_column(2, nolost=1), footprint.get_column(23, nolost=1), title='(Y Int)', yrange=[0,1])