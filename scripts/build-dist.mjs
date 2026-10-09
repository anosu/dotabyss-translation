// 构建 Vercel 加密分发目录（XOR + Base64，ENC: 前缀）。
// 读取 translations/，输出 dist/；密钥可用环境变量 DIST_KEY 覆盖，默认沿用 Vercel 密钥。
import { readdirSync, readFileSync, rmSync, mkdirSync, writeFileSync, copyFileSync } from 'node:fs'
import { join, relative, dirname } from 'node:path'

const KEY = process.env.DIST_KEY || 'c13an'
const TAG = 'ENC:'
const SOURCE = join(process.cwd(), 'translations')
const OUTPUT = join(process.cwd(), 'dist')

function xorBytes(data, key) {
    if (data.length === 0) return data
    const pad = (key.length - (data.length % key.length)) % key.length
    const padded = Buffer.concat([data, Buffer.alloc(pad)])
    const keyStream = Buffer.alloc(padded.length)
    for (let offset = 0; offset < padded.length; offset += key.length) {
        key.copy(keyStream, offset)
    }
    const view = BigInt(`0x${padded.toString('hex')}`)
    const mask = BigInt(`0x${keyStream.toString('hex')}`)
    return Buffer.from((view ^ mask).toString(16).padStart(padded.length * 2, '0'), 'hex').subarray(0, data.length)
}

function encryptJson(data, key, preserveBytes) {
    if (!preserveBytes) {
        data = Buffer.from(JSON.stringify(JSON.parse(data.toString('utf-8'))), 'utf-8')
    }
    return Buffer.from(TAG + xorBytes(data, Buffer.from(key, 'utf-8')).toString('base64'), 'ascii')
}

rmSync(OUTPUT, { recursive: true, force: true })
let count = 0

function walk(dir) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
        const file = join(dir, entry.name)
        if (entry.isDirectory()) {
            walk(file)
            continue
        }
        const rel = relative(SOURCE, file)
        const target = join(OUTPUT, rel)
        mkdirSync(dirname(target), { recursive: true })
        if (file.toLowerCase().endsWith('.json')) {
            const preserveBytes = entry.name === 'manifest.json' && dirname(file).endsWith('replacements')
            writeFileSync(target, encryptJson(readFileSync(file), KEY, preserveBytes))
        } else {
            copyFileSync(file, target)
        }
        count++
    }
}

walk(SOURCE)
console.log(`dist built: ${count} files, key=${KEY === 'c13an' ? 'Vercel default' : 'custom'}`)
