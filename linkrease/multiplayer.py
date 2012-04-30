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

import settings


def current_player():
    return settings.PLAYER[1]


def neutral_player():
    return settings.PLAYER[0]
