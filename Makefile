.PHONY: make clean run

make: run

clean:
	rm -f *.pyc
	rm -f chatIDToURL.txt
	rm -rf trackmaniaData
	rm -f TelegramBotSubscribers.txt

run:
	python main.py