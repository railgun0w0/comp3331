set xlabel "time [s]"
set ylabel "Throughput [Mbps]"
set key bel
plot  "tcp1.tr" u 1:2 t "tcp1" w lp lt rgb "blue", "tcp2.tr" u 1:2 t "tcp2" w lp lt rgb "red"
pause -1