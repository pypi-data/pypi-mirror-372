(* ::Package:: *)

(* :Title: PhysicalConstants *)

(* :Author: Stephen Wolfram *)

(* :Summary:
This package provides the values of various commonly used physical constants.
*)

(* :Package Version: 1.4 *)

(* :Copyright: Copyright 1988-2007, Wolfram Research, Inc. *)

(* :Context: Miscellaneous`PhysicalConstants` *)

(* :History:
	Version 1.1 by Stephen Wolfram (Wolfram Research), 1988.
	Revised by ECM (Wolfram Research), 1990, 1996, 1997.
	Added support for CosmicBackgroundTemperature, SolarSchwarzschildRadius,
	  GalacticUnit, and SolarLuminosity;  made minor changes in
	  values for ClassicalElectronRadius, EarthMass, EarthRadius,
	  ElectronComptonWavelength, GravitationalConstant, MolarGasConstant,
	  ThomsonCrossSection;  improved some usage messages.
	  Barbara Ercolano (Wolfram Research), 1997.
    Version 1.4, Adjusted values for CODATA 1998, John M. Novak, April 2000.
*)

(* :Keywords: *)

(* :Source:
    CODATA Recommended Values for the Fundamental Physical Constants: 1998,
      (Peter J. Mohr and Barry N. Taylor), http://physics.nist.gov/constants,
      also published in Journal of Physical and Chemical Reference Data,
      V28, N6, Dec. 1999 and Reviews of Modern Physics, V72, N2, Apr. 2000.
      (Cited in code below as CODATA 1998.)
    CRC Handbook of Chemistry and Physics, 80th Edition, (David R. Lide,
      editor-in-chief) 1999-2000. (Cited in code below as HCAP 80.)
 *)

(* :Warning: None. *)

(* :Mathematica Version: 4.0 *)

(* :Limitation: None. *)

(* :Discussion:
Note that all values are expressed in SI units, so that the
entire units package does not need to be loaded.

As of CODATA 1998, some conventions used for the electron and muon
g-factors, and for the electron, muon and neutron magnetic moments,
are different than before; they are all expressed as a negative
number in CODATA 1998, and a factor of two that was previously divided
out of the electron g-factor is present.

For the QuantizedHallConductance, HCAP 80 gives a value for e^2/h,
while CODATA 1998 gives a value for 2*e^2/h. I took the CODATA value
and divided out the factor of 2, to match the HCAP and the previous
use in this package.
*)

(* ======================== GENERAL CONSTANTS ======================== *)

(* Universal Constants *)

SpeedOfLight::usage =
"SpeedOfLight is the speed of light in a vacuum, a universal constant."
VacuumPermeability::usage =
"VacuumPermeability is the permeability of vacuum, a universal constant."
VacuumPermittivity::usage =
"VacuumPermittivity is the permittivity of vacuum, a universal constant."
GravitationalConstant::usage =
"GravitationalConstant is the coefficient of proportionality in Newton's law of \
gravitation."
AccelerationDueToGravity::usage =
"AccelerationDueToGravity is the acceleration of a body freely falling in a \
vacuum."
PlanckConstant::usage =
"PlanckConstant is a universal constant of nature which relates the energy \
of a quantum of radiation to the frequency of the oscillator which emitted it."
PlanckConstantReduced::usage =
"PlanckConstantReduced is PlanckConstant/(2 Pi), a universal constant."
PlanckMass::usage = "PlanckMass is a universal constant."

(* Electromagnetic Constants *)

ElectronCharge::usage =
"ElectronCharge is elementary charge, an electromagnetic constant."
MagneticFluxQuantum::usage =
"MagneticFluxQuantum is magnetic flux quantum, an electromagnetic constant."
QuantizedHallConductance::usage =
"QuantizedHallConductance is quantized Hall conductance, an \
electromagnetic constant."
(* BohrMagneton is Bohr magnetron, an electromagnetic constant.  But it
is also a unit of magnetic moment, so it is introduced only in Units.m, to
avoid shadowing. *)


(* =================== ATOMIC AND NUCLEAR CONSTANTS ==================== *)

FineStructureConstant::usage =
"FineStructureConstant is the fine structure constant, an atomic constant."
RydbergConstant::usage =
"RydbergConstant is an atomic constant appearing in the Rydberg formula \
expressing the wave-numbers of the lines in a spectral series."
BohrRadius::usage = "BohrRadius is the Bohr radius, an atomic constant."

(* Electron *)

ElectronMass::usage = "ElectronMass is the mass of an electron."
ElectronComptonWavelength::usage =
"ElectronComptonWavelength is the electron Compton wavelength, given by \
PlanckConstant/(ElectronMass SpeedOfLight)."
ClassicalElectronRadius::usage =
"ClassicalElectronRadius is the classical electron radius, an atomic constant."
ThomsonCrossSection::usage =
"ThomsonCrossSection is the Thomson cross section, an atomic constant."
ElectronMagneticMoment::usage =
"ElectronMagneticMoment is the electron magnetic moment."
ElectronGFactor::usage = "ElectronGFactor is the electron g-factor."

(* Muon *)

MuonMass::usage = "MuonMass is the mass of a muon."
MuonMagneticMoment::usage = "MuonMagneticMoment is the muon magnetic moment."
MuonGFactor::usage = "MuonGFactor is the muon g-factor."

(* Proton *)

ProtonComptonWavelength::usage =
"ProtonComptonWavelength the proton Compton wavelength, given by \
PlanckConstant/(ProtonMass SpeedOfLight)."
ProtonMagneticMoment::usage =
"ProtonMagneticMoment is the proton magnetic moment." (* scalar magnitude *)
ProtonMass::usage = "ProtonMass is the mass of a proton."

(* Neutron *)

NeutronComptonWavelength::usage =
"NeutronComptonWavelength the neutron Compton wavelength, given by \
PlanckConstant/(NeutronMass SpeedOfLight)."
NeutronMagneticMoment::usage =
"NeutronMagneticMoment is the neutron magnetic moment." (* scalar magnitude *)
NeutronMass::usage = "NeutronMass is the mass of a neutron."

(* Deuteron *)

DeuteronMass::usage = "DeuteronMass is the mass of a neutron."
DeuteronMagneticMoment::usage =
"DeuteronMagneticMoment is the deuteron magnetic moment."

(* Electroweak *)
WeakMixingAngle::usage = "WeakMixingAngle is a physical constant."

(* ==================== PHYSICO-CHEMICAL CONSTANTS ==================== *)

AvogadroConstant::usage =
"AvogadroConstant is the number of molecules in one mole or gram molecular \
weight of a substance."
FaradayConstant::usage =
"FaradayConstant is the product of the Avogadro constant (AvogadroConstant) \
and the elementary charge (ElectronCharge)."
MolarGasConstant::usage =
"MolarGasConstant is a physico-chemical constant."
BoltzmannConstant::usage =
"BoltzmannConstant is the ratio of the universal gas constant \
(MolarGasConstant) to Avogadro's number (AvogadroConstant)."
MolarVolume::usage =
"MolarVolume is the volume occupied by a mole or a gram molecular weight of any \
gas measured at standard conditions."
SackurTetrodeConstant::usage =
"SackurTetrodeConstant (absolute entropy constant), is a physico-chemical \
constant."
StefanConstant::usage =
"StefanConstant is the Stefan-Boltzmann constant, a universal constant of \
proportionality between the radiant emittance of a black body and the \
fourth power of the body's absolute temperature."

(* ======================== ASTRONOMICAL CONSTANTS ===================== *)

AgeOfUniverse::usage = "AgeOfUniverse is the age of the Universe, a physical \
constant."
CosmicBackgroundTemperature::usage=
"CosmicBackgroundTemperature is the temperature of the cosmic background \
radiation."
EarthMass::usage = "EarthMass is the mass of the Earth, a physical constant."
EarthRadius::usage = "EarthRadius is the radius of the Earth, a physical \
constant."
HubbleConstant::usage = "HubbleConstant is a measure of the rate at which the \
expansion of the universe varies with distance."
SolarRadius::usage = "SolarRadius is a physical constant."
SolarSchwarzschildRadius::usage =
"SolarSchwarzschildRadius is a physical constant."
SolarConstant::usage =
"SolarConstant is the rate at which solar radiation is received outside the \
earth's atmosphere on a surface normal to the incident radiation and at the \
earth's mean distance from the sun, integrated across all wavelengths. Also \
known as total solar irradiance."
GalacticUnit::usage =
"GalacticUnit is the approximate distance of the Sun from the center of the Milky Way \
Galaxy."
SolarLuminosity::usage = "SolarLuminosity is a physical constant."



(* ========================== OTHER CONSTANTS ========================== *)

SpeedOfSound::usage =
"SpeedOfSound is the speed of sound at sea level in the standard atmosphere."
IcePoint::usage =
"IcePoint is the temperature at which a mixture of air-saturated pure \
water and pure ice may exist in equilibrium at a pressure of one \
standard atmosphere."


Begin["`Private`"]

issueObsoleteFunMessage[fun_, context_] :=
        (Message[fun::obspkgfn, fun, context];
         )

AccelerationDueToGravity = 9.80665 Meter/Second^2 (* exact: HCAP 80, p. 1-6 *)

AgeOfUniverse = 4.7*^17 Second

AvogadroConstant = 6.02214199*^23 Mole^-1  (* CODATA 1998 *)

BohrRadius = 0.5291772083*^-10 Meter  (* infinite mass nucleus : CODATA 1998 *)

(* BohrMagnetron is introduced in Units.m...
BohrMagneton = 9.2740154*^-24 Ampere Meter^2
*)

BoltzmannConstant = 1.3806503*^-23 Joule/Kelvin  (* CODATA 1998 *)

CosmicBackgroundTemperature = 2.726 Kelvin

ClassicalElectronRadius = 2.817940285*^-15 Meter  (* CODATA 1998 *)

DeuteronMagneticMoment = 0.433073457*^-26 Joule/Tesla  (* CODATA 1998 *)

DeuteronMass = 3.34358309*^-27 Kilogram  (* CODATA 1998 *)

EarthMass = 5.9742*^24 Kilogram  (* HCAP 80, p. 14-3 *)

EarthRadius = 6378140 Meter   (* equatorial radius: HCAP 80, p. 14-1.
                                 The IUGG value for this is 6378136 m. *)

ElectronCharge = 1.602176462*^-19 Coulomb  (* CODATA 1998 *)

ElectronComptonWavelength = 2.426310215*^-12 Meter (* CODATA 1998 *)

ElectronGFactor = -2.0023193043737	(* -2(1+Subscript[\[Alpha], e]) : CODATA 1998 *)

ElectronMagneticMoment = -928.476362*^-26 Joule/Tesla  (* CODATA 1998 *)

ElectronMass = 9.10938188*^-31 Kilogram  (* CODATA 1998 *)

FaradayConstant = 96485.3415 Coulomb/Mole  (* CODATA 1998 *)

FineStructureConstant = 7.297352533*^-3  (* CODATA 1998 *)

GalacticUnit = 2.6*^20 Meter (* approximate value, 8.5 kPsc, derived from
                                 various atronomy texts; actual distance
                                 believed to vary from 8.4 to 9.7 kPsc *)

GravitationalConstant = 6.673*^-11 Newton Meter^2 Kilogram^-2  (* CODATA 1998 *)

HubbleConstant = 3.2*^-18 Second^-1

IcePoint = 273.15 Kelvin (* F-88 CRC Hdbk Chem & Phys, 68th Ed. *)

MagneticFluxQuantum = 2.067833636*^-15 Weber  (* h/(2 e) *) (* CODATA 1998 *)

MolarGasConstant = 8.314472 Joule Kelvin^-1 Mole^-1  (* CODATA 1998 *)

MolarVolume = 22.413996*^-3 Meter^3/Mole
    (* ideal gas, T = 273.15 K, P = 101.325 kPa : CODATA 1998 *)

MuonGFactor = -2.0023318320	(* CODATA 1998 *)

MuonMagneticMoment = -4.49044813*^-26 Joule/Tesla (* CODATA 1998 *)

MuonMass = 1.88353109*^-28 Kilogram  (* CODATA 1998 *)

NeutronComptonWavelength = 1.319590898*^-15 Meter (* CODATA 1998 *)

NeutronMagneticMoment = -0.96623640*^-26 Joule/Tesla (* CODATA 1998 *)

NeutronMass = 1.67492716*^-27 Kilogram  (* CODATA 1998 *)

PlanckConstant = 6.62606876*^-34 Joule Second  (* CODATA 1998 *)

PlanckConstantReduced = PlanckConstant / (2 Pi)  (* definition *)

PlanckMass = 2.1767*^-8 Kilogram  (* CODATA 1998 *)

ProtonComptonWavelength = 1.321409847*^-15 Meter (* CODATA 1998 *)

ProtonMagneticMoment = 1.410606633*^-26 Joule/Tesla (* CODATA 1998 *)

ProtonMass = 1.67262158*^-27 Kilogram  (* CODATA 1998 *)

QuantizedHallConductance = 3.874045848*^-5 Ampere/Volt (* e^2/h *)
   (* computed from CODATA 1998, which gives a value for 2*e^2/h *)

RydbergConstant = 10973731.568549 Meter^-1  (* CODATA 1998 *)

SackurTetrodeConstant = -1.1517048 (* 100 kPa : CODATA 1998 *)

SpeedOfLight = 299792458 Meter/Second  (* by definition: verified CODATA 1998 *)

SpeedOfSound = 340.29205 Meter/Second  (* standard atmosphere *)

SolarConstant = 1.3661*^3 Watt/Meter^2
    (* used in draft ISO standard DIS 21348, see "Status of ISO
       Draft International Standard for Determiing Solar Irradiances
       (DIS 21348)", Tobiska, W. Kent; Nusinov, Anatoliy A.,
       J. Adv. Space Research, in press. Note that this is not in
       fact a constant, but variabe over time, with a cycle imposed
       by the solar cycle. *)

SolarLuminosity = 3.84*^26 Watt  (* computed by definition from
      the SolarConstant, verified by literature citations. Definition
      is 4 Pi (1 AU)^2 * SolarConstant, given 1 AU in meters. *)

SolarRadius = 6.9599*^8 Meter  (* HCAP 80, p. 14-2 *)

SolarSchwarzschildRadius = 2.95325008*^3 Meter

StefanConstant = 5.670400*^-8 Watt Meter^-2 Kelvin^-4  (* CODATA 1998 *)

ThomsonCrossSection = 0.665245854*^-28 Meter^2  (* CODATA 1998 *)

VacuumPermeability = 4 Pi * 10^-7 Volt Second/Meter/Ampere  (* definition *)

VacuumPermittivity = 8.854187817*^-12 Ampere Second/Volt/Meter (* exact, definition *)

WeakMixingAngle = 0.2224    (* Sin[ThetaW]^2 : CODATA 1998*)

End[]

EndPackage[]
