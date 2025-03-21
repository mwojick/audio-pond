\include "articulate.ly"
\version "2.25.20"
\language "english"

\header {
  title = "Title"
  subtitle = "Subtitle"
  composer = "Composer"
  arranger = "Arranger"
  tagline = ""
}

global = {
  \numericTimeSignature
}

cd = \change Staff = "down"
cu = \change Staff = "up"

\parallelMusic voiceA,voiceB {
  \global
  % bar 1
  \key g \major
  \time 4/4
  \tempo 4 = 120
  \clef "G"
  g'8.( b'16 c'8 fs'4) 8 g'4 |
  \key g \major
  \time 4/4
  \tempo 4 = 120
  \clef "F"
  r4 g2.~ |

  % bar 2
  a''8 fs''8 c'8 fs'4 r8 g'4 |
  g2. r4 |

  % bar 3
  \key c \major
  b''8 f''8 <a' b'>16 b16 r8 g'2 |
  \key c \major
  e,4 r4 r2 |

  % bar 4
  r2 c'4 g'4 |
  g2 a4 g4 |

  \fine |
  \fine |
}

music = {
  \new PianoStaff \with { instrumentName = "Piano" }
  <<
    \new Staff = "up" { \voiceA }
    \new Staff = "down" { \voiceB }
  >>
}

\score {
  \music
  \layout {}
}

\score {
  \articulate
  \music
  \midi {}
}
