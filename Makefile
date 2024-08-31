all:
	make clean
	python open_terminal.py "make mapper0"
	python open_terminal.py "make mapper1"
	python open_terminal.py "make mapper2"
	python open_terminal.py "make mapper3"
	python open_terminal.py "make mapper4"
	python open_terminal.py "make reducer0"
	python open_terminal.py "make reducer1"
	python open_terminal.py "make reducer2"
	python open_terminal.py "make master"

master:
	python3 master.py

mapper0:
	python3 mapper.py --port 50050

mapper1:
	python3 mapper.py --port 50051

mapper2:
	python3 mapper.py --port 50052

mapper3:
	python3 mapper.py --port 50053

mapper4:
	python3 mapper.py --port 50054

mapper5:
	python3 mapper.py --port 50055

reducer0:
	python3 reducer.py --port 50060

reducer1:
	python3 reducer.py --port 50061

reducer2:
	python3 reducer.py --port 50062

reducer3:
	python3 reducer.py --port 50063

reducer4:
	python3 reducer.py --port 50064

reducer5:
	python3 reducer.py --port 50065

clean:
	rm -f Mappers/*/*.txt
	rm -f Reducers/*.txt
