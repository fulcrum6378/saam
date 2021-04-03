class SolarHijri {
    constructor(date) {
        this.Y = 0;
        this.M = 0
        this.D = 0;
        this.H = date.getHours();
        this.I = date.getMinutes();
        this.S = date.getSeconds();
        let y = date.getFullYear(), m = date.getMonth(), d = date.getDate(), l, clPl = new Date(), pl;
        if (SolarHijri.isLeap(y)) l = 1; else l = 0;
        clPl.setYear(y - 1);
        clPl.setMonth(0);
        clPl.setDate(1);
        if (SolarHijri.isLeap(clPl.getFullYear())) pl = 1; else pl = 0;
        switch (m) {
            case 0:
                if (d <= 20 - pl) {
                    this.Y = y - 622;
                    this.M = m + 9;
                    this.D = d + (10 + pl);
                } else {
                    this.Y = y - 622;
                    this.M = m + 10;
                    this.D = d - (20 - pl);
                }
                break;
            case 1:
                if (d <= 19 - pl) {
                    this.Y = y - 622;
                    this.M = m + 9;
                    this.D = d + (11 + pl);
                } else {
                    this.Y = y - 622;
                    this.M = m + 10;
                    this.D = d - (19 - pl);
                }
                break;
            case 2:
                if (d <= 20 - l) {
                    this.Y = y - 622;
                    this.M = m + 9;
                    this.D = d + (9 + l + pl);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (20 - l);
                }
                break;
            case 3:
                if (d <= 20 - l) {
                    this.Y = y - 621;
                    this.M = m - 3;
                    this.D = d + (11 + l);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (20 - l);
                }
                break;
            case 4:
            case 5:
                if (d <= 21 - l) {
                    this.Y = y - 621;
                    this.M = m - 3;
                    this.D = d + (10 + l);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (21 - l);
                }
                break;
            case 6:
            case 7:
            case 8:
                if (d <= 22 - l) {
                    this.Y = y - 621;
                    this.M = m - 3;
                    this.D = d + (9 + l);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (22 - l);
                }
                break;
            case 9:
                if (d <= 22 - l) {
                    this.Y = y - 621;
                    this.M = m - 3;
                    this.D = d + (8 + l);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (22 - l);
                }
                break;
            case 10:
                if (d <= 21 - l) {
                    this.Y = y - 621;
                    this.M = m - 3;
                    this.D = d + (9 + l);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (21 - l);
                }
                break;
            case 11:
                if (d <= 21 - l) {
                    this.Y = y - 621;
                    this.M = m - 3;
                    this.D = d + (9 + l);
                } else {
                    this.Y = y - 621;
                    this.M = m - 2;
                    this.D = d - (21 - l);
                }
                break;
        }
    }

    static isLeap(year) {
        return new Date(year, 1, 29).getDate() === 29;
    }
}