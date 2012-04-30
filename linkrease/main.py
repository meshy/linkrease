#This file is part of linkrease.

#linkrease is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#linkrease is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with linkrease.  If not, see <http://www.gnu.org/licenses/>.

from cocos.director import director

import settings
from scenes import IntroScene, MenuScene


def main():
    director.init(width=settings.SCR_W, height=settings.SCR_H, vsync=False)
    director.set_show_FPS(True)
    director.run(IntroScene() if not settings.SKIP_INTRO else MenuScene())


if __name__ == "__main__":
    import sys
    sys.exit(main())
