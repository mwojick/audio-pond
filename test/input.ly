% created by MidiToLily version 1.0.0.6
\version "2.24.3"
\language "english"
"track1" = \absolute {
  \key g \major
  \time 4/4
  \tempo 4 = 120
  \clef "G"
  g'8.( b'16 c'8 fs'4) 8 g'4 |
  a''8 fs''8 c'8 fs'4 r8 g'4 |
  \key c \major
  b''8 f''8 <a' b'>16 b16 r8 g'2 |
  r2 c'4 g'4 |
  \fine
}
"track2" = \absolute {
  \key g \major
  \time 4/4
  \tempo 4 = 120
  \clef "F"
  r4 g2.~ |
  g2. r4 |
  \key c \major
  e,4 r4 r2 |
  g2 a4 g4 |
  \fine
}
\score {
  <<
    \new Staff \"track1"
    \new Staff \"track2"
  >>
  \layout {}
  \midi {}
}