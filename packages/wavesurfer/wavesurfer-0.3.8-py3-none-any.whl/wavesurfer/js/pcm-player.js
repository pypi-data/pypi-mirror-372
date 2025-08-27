function getWavHeader(options) {
  const numFrames = options.numFrames
  const numChannels = options.numChannels || 2
  const sampleRate = options.sampleRate || 44100
  const bytesPerSample = options.isFloat? 4 : 2
  const format = options.isFloat? 3 : 1
  const blockAlign = numChannels * bytesPerSample
  const byteRate = sampleRate * blockAlign
  const dataSize = numFrames * blockAlign
  const buffer = new ArrayBuffer(44)
  const dv = new DataView(buffer)
  let p = 0
  function writeString(s) {
    for (let i = 0; i < s.length; i++) {
      dv.setUint8(p + i, s.charCodeAt(i))
    }
    p += s.length
  }
  function writeUint32(d) {
    dv.setUint32(p, d, true)
    p += 4
  }
  function writeUint16(d) {
    dv.setUint16(p, d, true)
    p += 2
  }
  writeString('RIFF')              // ChunkID
  writeUint32(dataSize + 36)       // ChunkSize
  writeString('WAVE')              // Format
  writeString('fmt ')              // Subchunk1ID
  writeUint32(16)                  // Subchunk1Size
  writeUint16(format)              // AudioFormat https://i.stack.imgur.com/BuSmb.png
  writeUint16(numChannels)         // NumChannels
  writeUint32(sampleRate)          // SampleRate
  writeUint32(byteRate)            // ByteRate
  writeUint16(blockAlign)          // BlockAlign
  writeUint16(bytesPerSample * 8)  // BitsPerSample
  writeString('data')              // Subchunk2ID
  writeUint32(dataSize)            // Subchunk2Size
  return new Uint8Array(buffer)
}

function getWavBytes(buffer, options) {
  const type = options.isFloat ? Float32Array : Int16Array
  const numFrames = buffer.byteLength / type.BYTES_PER_ELEMENT
  const headerBytes = getWavHeader(Object.assign({}, options, { numFrames }))
  const wavBytes = new Uint8Array(headerBytes.length + buffer.byteLength);
  wavBytes.set(headerBytes, 0)
  wavBytes.set(new Uint8Array(buffer), headerBytes.length)
  return wavBytes
}

(function() {
  if (typeof PCMPlayer === 'undefined') {
    class PCMPlayer {
      constructor(uuid, option) {
        this.uuid = uuid
        this.isDone = false  // 是否传输完毕
        this.isPlaying = true
        this.playButton = document.getElementById(`playButton-${uuid}`)
        this.playButton.onclick = () => {
          this.isPlaying ? this.pause() : this.play()
        }

        this.option = Object.assign({}, {channels: 1, sampleRate: 16000, flushTime: 100}, option)
        // 每隔 flushTime 毫秒调用一次 flush 函数
        this.interval = setInterval(this.flush.bind(this), this.option.flushTime)
        this.samples = new Int16Array()
        this.all_samples = new Int16Array()
        this.url

        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)()
        this.gainNode = this.audioCtx.createGain()
        this.gainNode.gain.value = 1.0  // 音量
        this.gainNode.connect(this.audioCtx.destination)
        this.startTime = this.audioCtx.currentTime
      }

      set sampleRate(rate) {
        this.option.sampleRate = rate
      }

      setDone() {
        this.isDone = true
      }

      feed(base64Data) {
        const binaryString = atob(base64Data)
        const buffer = new ArrayBuffer(binaryString.length)
        const bufferView = new Uint8Array(buffer)
        for (let i = 0; i < binaryString.length; i++) {
          bufferView[i] = binaryString.charCodeAt(i)
        }
        const data = new Int16Array(buffer)
        this.samples = new Int16Array([...this.samples, ...data])
        this.all_samples = new Int16Array([...this.all_samples, ...data])

        const wavBytes = getWavBytes(this.all_samples.buffer, {
          isFloat: false,
          numChannels: this.option.channels,
          sampleRate: this.option.sampleRate,
        })
        this.url = URL.createObjectURL(new Blob([wavBytes], { type: 'audio/wav' }))
      }

      flush() {
        if (!this.samples.length) return
        var bufferSource = this.audioCtx.createBufferSource()
        const length = this.samples.length / this.option.channels
        const audioBuffer = this.audioCtx.createBuffer(this.option.channels, length, this.option.sampleRate)
        for (let channel = 0; channel < this.option.channels; channel++) {
          const audioData = audioBuffer.getChannelData(channel)
          let offset = channel
          for (let i = 0; i < length; i++) {
            audioData[i] = this.samples[offset] / 32768
            offset += this.option.channels
          }
        }

        this.startTime = Math.max(this.startTime, this.audioCtx.currentTime)
        bufferSource.buffer = audioBuffer
        bufferSource.connect(this.gainNode)
        bufferSource.start(this.startTime)
        bufferSource.onended = () => {
          if (this.isDone && this.samples.length === 0 && this.startTime <= this.audioCtx.currentTime) {
            this.playButton.disabled = true
          }
        }
        this.startTime += audioBuffer.duration
        this.samples = new Int16Array()
      }

      async play() {
        await this.audioCtx.resume()
        this.playButton.innerHTML = '<i class="fa fa-pause"></i>'
        this.isPlaying = true
      }

      async pause() {
        await this.audioCtx.suspend()
        this.playButton.innerHTML = '<i class="fa fa-play"></i>'
        this.isPlaying = false
      }

      volume(volume) {
        this.gainNode.gain.value = volume
      }

      reset() {
        this.samples = new Int16Array(0)
        this.allSamples = new Int16Array(0)
        this.playButton.disabled = false
        this.isDone = false
        this.play()
      }

      destroy() {
        if (this.interval) {
          clearInterval(this.interval)
        }
        this.samples = null
        this.audioCtx.close()
        this.audioCtx = null
      }
    }
    window.PCMPlayer = PCMPlayer
  }
})()
