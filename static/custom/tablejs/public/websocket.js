websocket() {
        if (typeof window.wss == "undefined" || window.wss == false) {
          delete window.wss;
          window.wss = new WebSocket(${socketUrl});
        }
        window.wss.onmessage = data => {
          if (data.data) {
            this.result = JSON.parse(data.data);
            if (
              this.result.event == "game_open" &&
              this.game_code == this.result.game_code
            ) {
              this.wsRound = this.result.round;
              this.lotteryObj.last.number = this.result.arr;
            }
          }
        };
        window.wss.onclose = data => {
          window.wss = false;
          this.wsRound = "";
          setTimeout(() => {
            this.websocket();
          }, 3000);
        };
        window.wss.error = data => {
          window.wss = false;
          this.wsRound = "";
          setTimeout(() => {
            this.websocket();
          }, 3000);
        };
        this.over = () => {
          window.wss.close();
        };
      },