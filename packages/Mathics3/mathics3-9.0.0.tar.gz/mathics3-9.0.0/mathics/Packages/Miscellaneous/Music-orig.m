(* ::Package:: *)

(*:Mathematica Version: 2.0 *)

(*:Name: Miscellaneous`Music` *)

(*:Title: Music Functions *)

(*:Author: Arun Chandra (Wolfram Research), September 1992.  *)

(*:Summary:
This package provides functions for the manipulation and synthesis of scales.
It includes pitch/frequency equivalents.
*)

(*:Context: Miscellaneous`Music` *)

(*:Package Version: 1.0 *)

(* :Copyright: Copyright 1992-2007, Wolfram Research, Inc.
*)

(*:Reference: Usage messages only. *)

(*:Keywords: sound, music, synthesis, composition *)

(*:Requirements: A system on which Mathematica can produce sound. *)

(*:Warning: None. *)

(*:Sources: 
    Brun, Herbert. 1991. My Words and Where I Want Them. London:
        Princelet Editions.
    Dodge, Charles. 1985. Computer Music.  New York: Schirmer Books.
    Hiller, Lejaren A. 1963-66. Lectures on Musical Acoustics. Unpublished.
    Mathews, Max V. 1969. The Technology of Computer Music. 
        Cambridge, MA: MIT Press.
    Moore, F. Richard. 1990. Elements of Computer Music. 
        Englewood Cliffs, NJ: Prentice-Hall.
    Olson, Harry F. 1967. Music, Physics, and Engineering. 
        New York: Dover Publications, Inc.
    Wells, Thomas H. 1981. The Technology of Electronic Music. 
        New York: Schirmer Books.
*)

Message[General::newpkg, "Miscellaneous`Music`", "Music Package"]

BeginPackage["Miscellaneous`Music`"] ;

HertzToCents::usage =
"HertzToCents[flist] converts a list of frequencies measured in Hertz to a list \
of intervals measured in cents.";

CentsToHertz::usage =
"CentsToHertz[ilist] converts a list of intervals measured in cents to a \
list of frequencies measured in Hertz, beginning at 440 Hertz. \
CentsToHertz[ilist, f] gives a list of frequencies beginning at frequency f.";

Scale::usage =
"Scale[ilist, freq, dur] creates a Sound object corresponding to ilist, \
a list of intervals measured in cents, starting at freq Hertz and lasting \
dur seconds. Pre-defined interval lists are PythagoreanChromatic, \
PythagoreanMajor, JustMajor, JustMinor, MeanChromatic, MeanMajor, MeanMinor, \
TemperedChromatic, TemperedMajor, TemperedMinor, QuarterTone, and SixthTone.";

PythagoreanChromatic::usage = "PythagoreanChromatic is an interval list \
that is an extension of the PythagoreanMajor scale. It has 21 \
notes, since the complete scale requires 7 \"natural\" notes, 7 \
\"flat\" notes, and 7 \"sharp\" notes.";

PythagoreanMajor::usage = "PythagoreanMajor is an interval list in \
which the members of the scale are derived from a sequence of \
octaves and fifths, where a fifth is the ratio of 3/2 (702 cents) \
and an octave is the ratio of 2/1 (1200 cents). The scale is built \
by successive fifth addition and octave subtraction."; (* As
far as we know, PythagoreanMajor was invented in the 3rd or 4th
century, B.C.. *)

JustMajor::usage = "JustMajor is an interval list in which the ratios \
of the 3rd, 6th, and 7th intervals are simplified from the Pythagorean \
model. Whereas in the Pythagorean scale the ratios are 81/64 for a 3rd, \
27/16 for a 6th, and 243/128 for a 7th, in just intonation the ratios are \
5/4 for a 3rd, 5/3 for a 6th, and 15/8 for a 7th. The other intervals are \
the same as the Pythagorean scale. JustMajor was invented by the theorist \
Zarlino in the 16th century so that simultaneously sounding tones would have \
simple ratios.";

JustMinor::usage = "JustMinor is an interval list giving the minor \
version of the JustMajor scale.";

MeanChromatic::usage = "MeanChromatic is an interval list in which \
696.6 cents is used as the definition of a fifth, instead of 702 \
cents as in the Pythagorean and just intonation systems. This \
scale was invented in the 18th century by Gottfried Silbermann to \
correct for intonation problems due to enharmonic change.";

MeanMajor::usage = "MeanMajor is an interval list derived from the \
MeanChromatic scale.";

MeanMinor::usage = "MeanMinor is an interval list derived from the \
MeanChromatic scale.";

TemperedChromatic::usage = "TemperedChromatic is an interval list \
corresponding to equal-temperament in which the octave is divided into 12 \
equal parts.  Each part is a tempered semitone (100 cents). This is  \
equivalent to making 12 fifths equal to 7 octaves, so an equal-tempered  \
fifth is equal to 700 cents. (The just intonation and Pythagorean fifths \
are 702 cents, and the Mean Tone fifth is 696.6 cents.) This process \
guarantees equivalence between pitches, and allows intervals to be \
the same in all keys. However, except for the octave, none of the \
intervals is in tune with regard to mathematical ratios and the \
logic Pythagoras developed from proportional lengths of strings.";

TemperedMajor::usage = "TemperedMajor is an interval list derived \
from the TemperedChromatic scale.";

TemperedMinor::usage = "TemperedMinor is an interval list derived \
from the TemperedChromatic scale.";

QuarterTone::usage = "QuarterTone is an interval list in which each \
semitone (100 cents) is split in two.";

SixthTone::usage = "SixthTone is an interval list in which each \
semitone (100 cents) is split in three.";

Scan[(MessageName[Evaluate[ToExpression[#[[1]]<>#[[2]]]], "usage"] =
         #[[1]]<>#[[2]]<>" is the note "<>#[[1]]<>" in octave "<>#[[2]]<>".")&,
     Flatten[Outer[List,
     	{"A", "Asharp", "Bflat", "B", "Bsharp", "Cflat", "C", "Csharp", "Dflat",
	 "D", "Dsharp", "Eflat", "E", "Esharp", "Fflat", "F", "Fsharp", "Gflat",
         "G", "Gsharp", "Aflat"},
	{"0", "1", "2", "3", "4", "5", "6", "7"}], 1]]


Begin["`Private`"] ;

issueObsoleteFunMessage[fun_, context_] :=
        (Message[fun::obspkgfn, fun, context];
         )

Unprotect[Scale, PythagoreanChromatic, PythagoreanMajor, JustMajor, JustMinor,
    MeanChromatic, MeanMajor, MeanMinor, TemperedChromatic, TemperedMajor,
    TemperedMinor, QuarterTone, SixthTone, HertzToCents, CentsToHertz];

(*

    List of defined pitches

*)

If [ ! NumberQ[A1],
	notes = {"A", "Asharp", "B", "C", "Csharp", "D", "Dsharp", 
		"E", "F", "Fsharp", "G", "Gsharp"};
	Do[Evaluate[ToExpression[notes[[Mod[k-1,12]+1]] <>
			ToString[Ceiling[k/12]-1]]] = 27.5 2.^((k-1)/12), {k, 96}];
	Do[oct = ToString[k];
		Evaluate[ToExpression["Bsharp" <> oct]] = ToExpression["C" <> oct];
		Evaluate[ToExpression["Esharp" <> oct]] = ToExpression["F" <> oct];
		Evaluate[ToExpression["Cflat" <> oct]] = ToExpression["B" <> oct];
		Evaluate[ToExpression["Fflat" <> oct]] = ToExpression["E" <> oct];
		Evaluate[ToExpression["Bflat" <> oct]] = ToExpression["Asharp" <> oct];
		Evaluate[ToExpression["Dflat" <> oct]] = ToExpression["Csharp" <> oct];
		Evaluate[ToExpression["Eflat" <> oct]] = ToExpression["Dsharp" <> oct];
		Evaluate[ToExpression["Gflat" <> oct]] = ToExpression["Fsharp" <> oct];
		Evaluate[ToExpression["Aflat" <> oct]] = ToExpression["Gsharp" <> oct],
		{k, 0, 7}]
]

(*

    Set the default values for SampleRate, SampleDepth, and PlayRange.

*)

{sr, sd} = Switch[ $System,
        "NeXT", {22050, 16},
        "SPARC", {8000, 8},
        "Macintosh", {22254.5454, 8},
        "386", {11025, 8},
        "486", {11025, 8},
        _, {8192, 8}
];

Options[Scale] = { SampleRate -> sr, SampleDepth -> sd, 
	PlayRange -> {-1,1}, DisplayFunction->Identity};

(*

    Scale: All the following scales represent their intervals in
    cents, where 1200 cents == 1 octave.

*)

PythagoreanChromatic = {0,24,90,114,204,294,318,384,408,498,
    522,588,612,702,798,816,906,996,1020,1086,1110,1200};
PythagoreanMajor = {0,204,408,498,702,906,1110,1200};

JustMajor = {0,204,386.4,498,702,884.4,1088.4,1200};
JustMinor = {0,204,315.6,498,702,813.7,996.1,1200};

MeanChromatic = {0,76,193.2,310.3,386.3,503.4,579.5,
                696.6,772.6,889.7,1006.8,1082.9,1200};
MeanMajor = {0,193.2,386.3,503.4,696.6,889.7,1082.9,1200};
MeanMinor = {0,193.2,310.3,503.4,696.6,772.6,1006.8,1200};

TemperedChromatic = {0,100,200,300,400,500,600,700, 800,900,1000,1100,1200};
TemperedMajor = {0,200,400,500,700,900,1100,1200};
TemperedMinor = {0,200,300,500,700,800,1000,1200};

QuarterTone = {0,50,100,150,200,250,300,350,400,450,500,550,
                600,650,700,750,800,850,900,950,1000,1050,
                1100,1150,1200};

SixthTone = {0,33,66,100,133,166,200,233,266,300,333,366,
            400,433,466,500,533,566,600,633,666,700,733,
            766,800,833,866,900,933,966,1000,1033,1066,1100,
            1133,1166,1200};

isNumList[zlist_] := Return[ Apply[And, Map[NumberQ, zlist]] ] ;
Music::notnums = "Some members of the list `1` are not numbers.";

Scale::tooshort = "Interval list `` must have at least two members.";

Scale[ 
	i_?((VectorQ[#, NumberQ[N[#]]&])&),
	f_?((NumberQ[#])&), d_?((NumberQ[#])&), opts___] := 
		(issueObsoleteFunMessage[Scale,"Miscellaneous`Music`"];
	With[ { out = scale[i, f, d, opts] }, 
			out /; out =!= $Failed ] /; Length[i] >= 2)
	

scale[ Intervals_, startingFreq_, totalDuration_, opts___ ] :=

  Module[
    {intervalList, noteDuration, sr, sd, pr, id, mypi},

	{ sr, sd, pr, id } =
        {SampleRate, SampleDepth, PlayRange, DisplayFunction} 
			/. {opts} /. Options[Scale];

    intervalList = Map[(N[startingFreq * 10^(#/(1200/Log[10,2]))])&, Intervals];
    noteDuration = Length[intervalList]/totalDuration;
	mypi = N[2 Pi] ;

    Play[ Sin[ mypi t intervalList[[ 1+Floor[t * noteDuration] ]] ],
          {t,0,totalDuration-.000001},
		SampleRate->sr, SampleDepth->sd, PlayRange->pr, DisplayFunction->id ]
]

h2c[x_, y_] := N[ 3986.313714 * ( Log[10, y] - Log[10, x] ) ] ;

HertzToCents[hlist_?((VectorQ[#, NumberQ[N[#]]&])&)] := 
	(issueObsoleteFunMessage[HertzToCents,"Miscellaneous`Music`"];
	Apply[(h2c[#1,#2])&, Partition[hlist, 2, 1],{1}] /; Length[hlist] >= 2)


CentsToHertz[clist_?((VectorQ[#, NumberQ[N[#]]&])&), f_:440] := 
	(issueObsoleteFunMessage[CentsToHertz,"Miscellaneous`Music`"];
	Map[(N[f * 10^(#/(1200/Log[10,2]))])&, clist] /; 
					Length[clist] >= 2 && NumberQ[N[f]])


(*

        Protect all user-accessible functions.

*)

Protect[Scale, PythagoreanChromatic, PythagoreanMajor, JustMajor, JustMinor,
    MeanChromatic, MeanMajor, MeanMinor, TemperedChromatic, TemperedMajor,
    TemperedMinor, QuarterTone, SixthTone, HertzToCents, CentsToHertz];

End[] ;

EndPackage[] ;




