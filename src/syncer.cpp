#include "syncer.h"

void revolution::Syncer::run() {  // TODO: ADD PROGRAM LOGIC
}

unsigned int revolution::Syncer::getPriority() {
	return priority_;
}

revolution::Syncer::Syncer() : App{"syncer"} {} // TODO: DO NOT HARD-CODE

int main() {
	revolution::Syncer &syncer = revolution::Syncer::getInstance();

	syncer.run();

	return 0;
}
